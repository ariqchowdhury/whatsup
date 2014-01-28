
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.webbitserver.WebServer;
import org.webbitserver.BaseWebSocketHandler;
import org.webbitserver.WebSocketConnection;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import static org.webbitserver.WebServers.createWebServer;

public class WS extends BaseWebSocketHandler {
	
	private Map<String, List<WebSocketConnection>> channel_collection = Collections.synchronizedMap(new HashMap<String, List<WebSocketConnection>>()); 
	
	public void onOpen(WebSocketConnection connection) {
		System.out.println("open");
	}
	
	public void onClose(WebSocketConnection connection) {
		System.out.println("close: " + connection.data("chid"));
		channel_collection.get(connection.data("chid")).remove(connection);
		//channel_collection.get()
		//find connection and remove it from the channel_collection
	}
	
	public void onMessage(WebSocketConnection connection, String message) throws ParseException {
		//System.out.println(message);
				
		JSONParser parser = new JSONParser();

		Object obj = parser.parse(message);

		JSONObject jsonObject = (JSONObject) obj;
		
		String type = (String) jsonObject.get("type");

		if (type.equals("init")) {
			String ch_key = (String) jsonObject.get("msg");
			//WhatsupConnection ws = new WhatsupConnection(connection);
			//ws.ch_id = ch_key;
			
			connection.data("chid", ch_key);
			
			if (channel_collection.containsKey(ch_key)) {
				channel_collection.get(ch_key).add(connection);
			}
			else {
				List<WebSocketConnection> users = Collections.synchronizedList(new LinkedList<WebSocketConnection>());
				users.add(connection);
				channel_collection.put(ch_key, users);
			}
			
		}
		else if (type.equals("msg")) {
			//broadcast
			String ch_key = (String) jsonObject.get("src");
			String msg = (String) jsonObject.get("msg");
			String user = (String) jsonObject.get("user");
							
			JSONObject outgoing_message = new JSONObject();
			outgoing_message.put("msg", msg);
			outgoing_message.put("user", user);
			outgoing_message.put("ts", "10:00");
				
			String json_outgoing_message = outgoing_message.toJSONString();
			
			long startTime = System.currentTimeMillis();
			
			for (WebSocketConnection client : channel_collection.get(ch_key)) {
				client.send(json_outgoing_message);
			}
			long stopTime = System.currentTimeMillis();
			long elapsedTime = stopTime - startTime;
			System.out.println(elapsedTime+"ms");
		}	
		
	}
	
	public static void main(String[] args) {
		WebServer webServer = createWebServer(9000)
             .add("/ws", new WS());
	
		webServer.start();
		System.out.println("Server running at " + webServer.getUri());
	}
}
