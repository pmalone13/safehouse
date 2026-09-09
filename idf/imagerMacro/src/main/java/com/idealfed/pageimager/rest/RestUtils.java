package com.idealfed.pageimager.rest;
import java.io.BufferedReader;
import java.io.Console;
import java.io.DataOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class RestUtils {

	public static String callPost(String inUrl, String inPayload, String inJsessionId)
	{
	   String retStr = "";

		StringBuffer sb = new StringBuffer();
		try
		{

			String uri =  inUrl; //"http://jira.idealfed.com/rest/auth/1/session";
			URL url = new URL(uri);
			String urlParameters  = inPayload; //"{\"username\":\"johndoe\",\"password\":\"johndoe\"}";
			byte[] postData       = urlParameters.getBytes(StandardCharsets.UTF_8 );
			int postDataLength = postData.length;
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setDoOutput( true );
			conn.setInstanceFollowRedirects( false );
			conn.setRequestMethod( "POST" );
			conn.setRequestProperty( "Content-Type", "application/json");
			conn.setRequestProperty( "charset", "utf-8");
			conn.setRequestProperty( "Content-Length", Integer.toString( postDataLength ));
			if(inJsessionId!=null)	conn.setRequestProperty("Cookie", "JSESSIONID="+inJsessionId);
			conn.setUseCaches( false );
		    DataOutputStream wr = new DataOutputStream( conn.getOutputStream());
		    wr.write( postData );
		    InputStream inJson = conn.getInputStream();
	        Reader in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));

	        for (int c; (c = in.read()) >= 0;) sb.append((char)c);
		    in.close();

			}
		catch(Exception e)
		{
			//System.out.println(e.getMessage());
			sb.append(e.getMessage());
		}
	   return sb.toString();
	}


	public static String callGet(String inUrl, String inSessionId)
	{
	   String retStr = "";

		StringBuffer sb = new StringBuffer();
		try
		{

			String uri =  inUrl; //"http://jira.idealfed.com/rest/auth/1/session";
			URL url = new URL(uri);
		    String oCookie = "JSESSIONID="+inSessionId;
		    //if(!xref.equals("")) oCookie += "; atlassian.xsrf.token="+xref;
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setInstanceFollowRedirects( false );
			conn.setRequestMethod( "GET" );
			conn.setRequestProperty( "Content-Type", "application/json");
			conn.setRequestProperty( "charset", "utf-8");
			conn.setRequestProperty("Cookie", oCookie);
			conn.setUseCaches( false );


		     BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
		      String line;
			 while ((line = rd.readLine()) != null) {
		         sb.append(line);
		      }
		      rd.close();
		}
		catch(Exception e)
		{
			//System.out.println(e.getMessage());
			sb.append(e.getMessage());
		}

	   return sb.toString();
	}

}