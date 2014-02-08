import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.webbitserver.WebServer;
import org.webbitserver.BaseWebSocketHandler;
import org.webbitserver.WebSocketConnection;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.FutureTask;
import java.net.URISyntaxException;
import java.security.NoSuchAlgorithmException;
import java.security.KeyManagementException;
import java.util.UUID;

import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Channel;

import static org.webbitserver.WebServers.createWebServer;

public class WhatsupSocket extends BaseWebSocketHandler {
	
	private Map<String, List<WebSocketConnection>> channel_collection = Collections.synchronizedMap(new HashMap<String, List<WebSocketConnection>>());
	
	private ConnectionFactory factory;
	private Connection conn;
	private Channel channel;

	private String exchangeName = "celery";
	private String queueName = "celery";
	private String routingKey = "celery";

	private String task_queue_test = "whatsup.task_queue.test";
	private String task_queue_write_comment_to_db = "whatsup.task_queue.write_to_db";

	WhatsupSocket() throws IOException {
		super();
		factory = new ConnectionFactory();
		
		try {
			factory.setUri("amqp://guest@localhost:5672");
		}
		catch (URISyntaxException e) {
			// TODO: log error message
			e.printStackTrace();
			return;
		}
		catch (NoSuchAlgorithmException e) {
			// TODO: log error message
			e.printStackTrace();
			return;
		}
		catch (KeyManagementException e) {
			// TODO: log error message
			e.printStackTrace();
			return;
		}

		
		conn = factory.newConnection();
		channel = conn.createChannel();
	
		channel.exchangeDeclare(exchangeName, "direct", true);
		channel.queueDeclare(queueName, true, false, false, null);
		channel.queueBind(queueName, exchangeName, routingKey);

	}

	public void onOpen(WebSocketConnection connection) {
		//System.out.println("New connection");
		
	}
	
	@SuppressWarnings("unchecked")
	public void onClose(WebSocketConnection connection) {
		JSONObject usr_cnt_msg = new JSONObject();
		String ch_key = (String) connection.data("chid");
		// Connection holds which chid it belongs to, so use that to find it in the hash and then remove it
		channel_collection.get(ch_key).remove(connection);
		int num_users = channel_collection.get(ch_key).size();
		usr_cnt_msg.put("num_users", num_users);
		
		ParaBroadcastMsg(usr_cnt_msg.toJSONString(), ch_key);
		//System.out.println("CLOSED connection");
	}
	
	@SuppressWarnings("unchecked")
	public void onMessage(WebSocketConnection connection, String message) {
		//System.out.println(message);
				
		JSONParser parser = new JSONParser();
		Object obj;
		try  {
			obj = parser.parse(message);
		}
		catch (ParseException e) {
			// Parse exception likely means message coming from outside source/websocket connection
			// TODO: log error message
			e.printStackTrace();
			return;
		}
		JSONObject jsonObject = (JSONObject) obj;
		String type = (String) jsonObject.get("type");
		
		int num_users;
		JSONObject usr_cnt_msg = new JSONObject();

		if (type.equals("init")) {
			String ch_key = (String) jsonObject.get("msg");
			
			connection.data("chid", ch_key);
			
			if (channel_collection.containsKey(ch_key)) {
				channel_collection.get(ch_key).add(connection);				
			}
			else {
				List<WebSocketConnection> users = Collections.synchronizedList(new ArrayList<WebSocketConnection>(550));
				users.add(connection);
				channel_collection.put(ch_key, users);
			}
			
			num_users = channel_collection.get(ch_key).size();
			usr_cnt_msg.put("num_users", num_users);
			
			ParaBroadcastMsg(usr_cnt_msg.toJSONString(), ch_key);
			
		}
		else if (type.equals("msg")) {
			//broadcast
			String src = (String) jsonObject.get("src");
			String msg = (String) jsonObject.get("msg");
			String user = (String) jsonObject.get("user");
							
			JSONObject outgoing_message = new JSONObject();
			outgoing_message.put("msg", msg);
			outgoing_message.put("user", user);
			outgoing_message.put("ts", "12:34");
				
			final String json_outgoing_message = outgoing_message.toJSONString();
			
			final WebSocketConnection conn = connection;
				
			ParaBroadcastMsg(json_outgoing_message, src);
			
			// sanitized msg should escape out string quotes
			String sanitized_msg = "\'" + msg + "\'";
			
			WriteCommentToDatabase(user, sanitized_msg, src);

		}	
		
	}
	
	@SuppressWarnings("unchecked")
	public void WriteCommentToDatabase(String user, String sanitized_msg, String src) {
		String uuid = UUID.randomUUID().toString();
		String comment_id = UUID.randomUUID().toString();

		JSONArray arg_list = new JSONArray();
		arg_list.add(user);
		arg_list.add(sanitized_msg);
		arg_list.add(src);
		arg_list.add(comment_id);

		JSONObject celery_msg = new JSONObject();
		celery_msg.put("id", uuid);
		celery_msg.put("task", task_queue_write_comment_to_db);
		celery_msg.put("args", arg_list);

		String message_body = celery_msg.toJSONString();

		try {
			channel.basicPublish(exchangeName, routingKey, 
								 new AMQP.BasicProperties.Builder()
								 	.contentType("application/json").userId("guest").build(),
								 	 message_body.getBytes("ASCII"));
		}
		catch (IOException e) {
			// Something wrong with connection to rabbitmq server
			// TODO: log error message
			e.printStackTrace();
			return;
		}
	}
	
	public Void ParaBroadcastMsg(final String msg, String src) {
		int num_threads = 2;
		
		ExecutorService executor = Executors.newFixedThreadPool(num_threads);
		List<FutureTask<Void>> task_list = new ArrayList<FutureTask<Void>>();
		
		List<WebSocketConnection> full_list = channel_collection.get(src);
		int list_size = full_list.size();
		
		if (list_size < num_threads) {
			
			for (WebSocketConnection client : channel_collection.get(src)) {
				client.send(msg);
			}
		}
		else {
		
			int mid_point = list_size / num_threads;
			
			final List<WebSocketConnection> sublist_1 = full_list.subList(0, mid_point);
			final List<WebSocketConnection> sublist_2 = full_list.subList(mid_point, list_size);
			
			FutureTask<Void> ft1 = new FutureTask<Void>(new Callable<Void>() {
				@Override
				public Void call() {
					return WhatsupSocket.BroadcastMsg(sublist_1, msg);
				}
			});
			
			task_list.add(ft1);
			executor.execute(ft1);
			
			FutureTask<Void> ft2 = new FutureTask<Void>(new Callable<Void>() {
				@Override
				public Void call() {
					return WhatsupSocket.BroadcastMsg(sublist_2, msg);
				}
			});
			
			task_list.add(ft2);
			executor.execute(ft2);
			
			task_list.get(0);
			task_list.get(1);
			executor.shutdown();
		}
		return null;
	}
	
	public static Void BroadcastMsg(List<WebSocketConnection> conn, String msg) {
		for (WebSocketConnection client : conn) {
			client.send(msg);
		}
		
		return null;
	}
	
	public static void main(String[] args) {
		WebServer webServer = null;
		try {
			webServer = createWebServer(9000)
	             .add("/ws", new WhatsupSocket());
        }
        catch (IOException e) {
        	System.out.println("Problem with Celery connection");
        	System.exit(0);
        }
	
		webServer.start();
		System.out.println("Server running at " + webServer.getUri());
	}
}