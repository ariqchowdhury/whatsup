
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.webbitserver.WebServer;
import org.webbitserver.BaseWebSocketHandler;
import org.webbitserver.WebSocketConnection;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import static org.webbitserver.WebServers.createWebServer;

public class WS extends BaseWebSocketHandler {
	
	private Map<String, List<WebSocketConnection>> channel_collection = Collections.synchronizedMap(new HashMap<String, List<WebSocketConnection>>());
		
	public void onOpen(WebSocketConnection connection) {
		
	}
	
	public void onClose(WebSocketConnection connection) {
		// Connection holds which chid it belongs to, so use that to find it in the hash and then remove it
		channel_collection.get(connection.data("chid")).remove(connection);
	}
	
	public void onMessage(WebSocketConnection connection, String message) throws ParseException, IOException {
		//System.out.println(message);
				
		JSONParser parser = new JSONParser();

		Object obj = parser.parse(message);

		JSONObject jsonObject = (JSONObject) obj;
		
		String type = (String) jsonObject.get("type");

		if (type.equals("init")) {
			String ch_key = (String) jsonObject.get("msg");
			
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
			String src = (String) jsonObject.get("src");
			String msg = (String) jsonObject.get("msg");
			String user = (String) jsonObject.get("user");
							
			JSONObject outgoing_message = new JSONObject();
			outgoing_message.put("msg", msg);
			outgoing_message.put("user", user);
			outgoing_message.put("ts", "10:00");
				
			String json_outgoing_message = outgoing_message.toJSONString();
			
			long startTime = System.currentTimeMillis();
			
			for (WebSocketConnection client : channel_collection.get(src)) {
				client.send(json_outgoing_message);
			}
			long stopTime = System.currentTimeMillis();
			long elapsedTime = stopTime - startTime;
			System.out.println(elapsedTime+"ms");
								
			// sanitized msg should escape out string quotes
			String sanitized_msg = "\'" + msg + "\'";
			
			//Write comment to database			
			Process p = Runtime.getRuntime().exec(new String[] {"python", "src/j_write_db.py", user, sanitized_msg, src});
			BufferedReader stdInput = new BufferedReader(new InputStreamReader(p.getInputStream()));
			BufferedReader stdError = new BufferedReader(new InputStreamReader(p.getErrorStream()));
			
			String s = null;
			while ((s = stdInput.readLine()) != null) {
				System.out.println(s);
			}
			while ((s = stdError.readLine()) != null) {
				System.out.println(s);
			}
		}	
		
	}
	
	public static void main(String[] args) throws IOException {
		WebServer webServer = createWebServer(9000)
             .add("/ws", new WS());
	
		webServer.start();
		System.out.println("Server running at " + webServer.getUri());
	}
}
