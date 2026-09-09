package com.idealfed.pageimager.rest;

import java.io.BufferedReader;
import java.io.Console;
import java.io.DataOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import com.atlassian.core.util.StringUtils;
import org.json.JSONArray;
import org.json.JSONObject;
import com.atlassian.applinks.api.ApplicationLink;
import com.atlassian.applinks.api.ApplicationLinkRequest;
import com.atlassian.applinks.api.ApplicationLinkRequestFactory;
import com.atlassian.applinks.api.ApplicationLinkService;
import com.atlassian.applinks.api.ApplicationLinkResponseHandler;
import com.atlassian.sal.api.net.Request;
import com.atlassian.sal.api.net.Request.MethodType;
import com.atlassian.sal.api.net.Response;
import com.atlassian.sal.api.net.ResponseException;
import com.atlassian.sal.api.net.ResponseHandler;
import com.atlassian.applinks.api.CredentialsRequiredException;

import com.atlassian.applinks.api.application.jira.JiraApplicationType;

public class StructureUtils {
    private static final Log log=LogFactory.getLog(StructureUtils.class);

	private static String baseUrl = "http://jira.idealfed.com";
	private static String username = "johndoe";
	private static String password = "johndoe";

    private static String initializeLink(ApplicationLinkService applicationLinkService)
    {
		//this is where you need to login and call the api
		String iUrl =  "/rest/api/2/myself";
		ApplicationLink jiraLink = applicationLinkService.getPrimaryApplicationLink(JiraApplicationType.class);
		ApplicationLinkResponseHandler alrh = null;
		if(jiraLink != null)
		{
			String outStr = null;
			final ApplicationLinkRequestFactory requestFactory = jiraLink.createAuthenticatedRequestFactory();
			try {
				ApplicationLinkRequest request = requestFactory.createRequest(MethodType.GET,"");
				request.setRequestContentType("application/json");
				//request.setRequestBody("Set your json as string here);

				outStr = request.execute(new ApplicationLinkResponseHandler<String>()
				{
					@Override
					public String credentialsRequired(Response response) throws ResponseException
					{
						throw new ResponseException(new CredentialsRequiredException(requestFactory, "Token is invalid"));
					}
					@Override
					public String handle(Response response) throws ResponseException
					{
						//return response.getResponseBodyAsString();
						 Map<String, String> myHeads = response.getHeaders();
						 String os = "";
						 for (Map.Entry<String, String> pair : myHeads.entrySet()) {
							os += pair.getKey() + " " + pair.getValue() + "\n";
						 }
					     return "here";
					}
				});
			} catch (CredentialsRequiredException e) {
				outStr = e.getMessage();
			} catch (Exception e){
				outStr= e.getMessage();
			}finally {
				return outStr;
			}
		}
		return "no jira link";
	}

	public static String getStructure(String inPage, ApplicationLinkService applicationLinkService) {

		String inS =  inPage; //"<p>Some stuff</p><p><ac:structured-macro ac:name=\"gadget\" ac:schema-version=\"1\" ac:macro-id=\"81029b2f-2c57-483e-baa0-c38e3fa87c78\"><ac:parameter ac:name=\"preferences\">structureId=2&amp;viewId=4&amp;filterType=none&amp;filterQuery=&amp;filterId=&amp;customTitle=&amp;numRows=45&amp;allowChanges=true&amp;canvas-viewId=&amp;canvas-numRows=10&amp;isConfigured=true&amp;useCanvasSettings=false</ac:parameter><ac:parameter ac:name=\"url\">http://jira.idealfed.com/rest/gadgets/1.0/g/com.almworks.jira.structure:structure-gadget/gadgets/structure-gadget.xml</ac:parameter></ac:structured-macro></p><p><br /></p><p>end of page.</p><p><br /></p><p><br /></p>";

		Map<String, Map> myGadgets = new HashMap<String, Map>();
		Map<String, Map> myKeys = new HashMap<String, Map>();

		String outStr = inS;
		Pattern outerPattern = Pattern.compile("<ac:structured-macro(.*?)<\\/ac:structured-macro>");
		Pattern innerPattern = Pattern.compile("<ac:parameter ac:name=\"preferences\">(.*?)<\\/ac:parameter>");
		Matcher m = outerPattern.matcher(inS);
		int gindex = 0;
		while (m.find()) {
		    String s = m.group(1);
		    //s is EACH structure component
		    Matcher m2 = innerPattern.matcher(s);
		    while (m2.find()){
		    	String s2 = m2.group(1);
		    	String[] pars = s2.split("&amp;");
		    	Map<String, String> myParams = new HashMap<String, String>();
		    	for(int i=0; i< pars.length;i++)
	    		{
		    		String[] nvp = pars[i].split("=");
		    		if(nvp.length>1) myParams.put(nvp[0], nvp[1]);
		    		else myParams.put(nvp[0], "");
		    	}

		    	for (Map.Entry<String, String> entry: myParams.entrySet()) {
		    	    String key =  entry.getKey();
		    	    String value = entry.getValue();
		    	    //System.out.println(key + " is " + value);
		    	}
		    	outStr = outStr.replaceFirst("<ac:structured-macro(.*?)<\\/ac:structured-macro>","structureGadget_"+gindex);
		    	myGadgets.put("structureGadget_"+gindex, myParams);
		    	gindex++;
		    	break;
		    }
		}
		String retStr="";
		String jSessionId = "";
		String tLogin ="";
		String baseStructure = "";
		String forest = "";
		String content = "";
		StringBuilder outTable = null;

		//Loop each gadget
		gindex=0;
		for (Map.Entry<String, Map> entry: myGadgets.entrySet()) {
			Map myG = entry.getValue();
			outTable = new StringBuilder();
			try
			{
                 log.error("Going to test the link");
				String testLink = StructureUtils.initializeLink(applicationLinkService);
                 log.error("Link Result: " + testLink);

				tLogin = RestUtils.callPost(baseUrl + "/rest/auth/1/session","{\"username\":\""+username+"\",\"password\":\""+password+"\"}",null);
				JSONObject obj = new JSONObject(tLogin);
				JSONObject session = obj.getJSONObject("session");
				jSessionId = session.getString("value");
				baseStructure = RestUtils.callGet(baseUrl + "/rest/structure/2.0/structure/" + myG.get("structureId").toString(), jSessionId);
				// var forestUrl = '/rest/structure/2.0/forest/latest?s={"structureId":'+sId+',"title":true}';
				forest =RestUtils.callGet(baseUrl + "/rest/structure/2.0/forest/latest?s=%7B\"structureId\":"+myG.get("structureId").toString()+",\"title\":true%7D", jSessionId);
				//forest = RestUtils.callGet(baseUrl + "/rest/structure/2.0/structure/" + myG.get("structureId").toString(), jSessionId);

				JSONObject forObj = new JSONObject(forest);
				String formula = forObj.getString("formula");

				int ctr = -1;
				String[] fParts = formula.split(",");
				String iKeys[] = new String[fParts.length-1];
				Map<String, String> myKeyParts;
				for(int i=1;i<fParts.length;i++)
				{
					String[] inParts = fParts[i].split(":");
					myKeyParts = new HashMap<String, String>();
					iKeys[i-1]=inParts[0];
					myKeyParts.put("id", inParts[0]);
					myKeyParts.put("depth", inParts[1]);
					myKeyParts.put("identity", inParts[2]);
					myKeys.put(inParts[0], myKeyParts);
				}

				/* attributes = [
				{"id":"key","format":"text"},
				{"id":"summary","format":"text"},
				{"id":"project","format":"id"},
				{"id":"issuetype","format":"id"},
				{"id":"done","format":"boolean"},
				{"id":"progress","format":"number","params":{"basedOn":"timetracking","resolvedComplete":true,"includeSelf":true}},
				{"id":"status","format":"html"},
				{"id":"timeestimate","format":"html"},
				{"id":"sum","format":"html","params":{"attribute":{"id":"timeestimate","format":"duration"}}},{"id":"timespent","format":"html"},
				{"id":"sum","format":"html","params":{"attribute":{"id":"timespent","format":"duration"}}}
				 ];*/

				String attributes = "[{\"id\":\"key\",\"format\":\"text\"},{\"id\":\"summary\",\"format\":\"text\"},{\"id\":\"project\",\"format\":\"id\"},{\"id\":\"issuetype\",\"format\":\"id\"},{\"id\":\"done\",\"format\":\"boolean\"},{\"id\":\"progress\",\"format\":\"number\",\"params\":{\"basedOn\":\"timetracking\",\"resolvedComplete\":true,\"includeSelf\":true}},{\"id\":\"status\",\"format\":\"html\"},{\"id\":\"timeestimate\",\"format\":\"html\"},{\"id\":\"sum\",\"format\":\"html\",\"params\":{\"attribute\":{\"id\":\"timeestimate\",\"format\":\"duration\"}}},{\"id\":\"timespent\",\"format\":\"html\"},{\"id\":\"sum\",\"format\":\"html\",\"params\":{\"attribute\":{\"id\":\"timespent\",\"format\":\"duration\"}}}]";
				JSONArray attArray = new JSONArray(attributes);
				String payloadData = "{\"requests\":[{\"forestSpec\":{\"structureId\":"+myG.get("structureId").toString()+",\"title\":true},\"rows\":[rowKeysArray],\"attributes\":"+attributes+"}]}";


			    payloadData=payloadData.replace("rowKeysArray",String.join(",",iKeys));
				content = RestUtils.callPost(baseUrl + "/rest/structure/2.0/value",payloadData,jSessionId);

				//get to content array
				JSONObject contentObj = new JSONObject(content);
				JSONArray responses =contentObj.getJSONArray("responses");
				JSONObject responseOne = responses.getJSONObject(0);
				JSONArray data1 = responseOne.getJSONArray("data");

				outTable.append("<table cellpadding='3' cellspacing='0' style='font-size:10pt'><tr>");
				for(int i=0;i<attArray.length();i++)
				{
					JSONObject  s = attArray.getJSONObject(i);
					if(s.getString("id").equals("project")) continue;
		            if(s.getString("id").equals("issuetype")) continue;
		            if(s.getString("id").equals("sum"))
		            {
		            	outTable.append("<td style='background:darkgreen !important;color:black;border-bottom:solid black 1px;width:80px'>Sum of "+s.getJSONObject("params").getJSONObject("attribute").getString("id") +"</td>");
		            }
		            else
		            {
		            	if(s.getString("id").equals("summary"))
				        	  outTable.append("<td style='background-color:darkgreen;color:black;border-bottom:solid black 1px;width:200px'>"+s.getString("id")+"</td>");
				         else
				        	 outTable.append("<td style='background-color:darkgreen;color:black;border-bottom:solid black 1px;width:80px'>"+s.getString("id")+"</td>");
		            }
				}
				outTable.append("</tr>");


				for(int i=0;i<iKeys.length;i++)
				{
					String r = iKeys[i];
					outTable.append("<tr>");
					for(int j=0;j<attArray.length();j++)
					{
						JSONObject  s = attArray.getJSONObject(j);
						if(s.getString("id").equals("project")) continue;
			            if(s.getString("id").equals("issuetype")) continue;

			            int rIndex = Arrays.asList(iKeys).indexOf(r);
			            String oData = getValue(data1,s, r, rIndex,myKeys);
			            outTable.append("<td style=\"white-space: nowrap\">"+oData+"</td>");
					}
					outTable.append("</tr>");
				}
				outTable.append("</table>");

			}
			catch(Exception e)
			{
				outTable.append(e.getMessage());
			}

			//finally, replace the temp string in the out str with the new table
			outStr = outStr.replaceFirst("structureGadget_"+gindex, outTable.toString());
			gindex++;

			//now convert the outstring....
			//System.out.println(outStr);
			//System.out.println(jSessionId);
			//System.out.println(baseStructure);
			//System.out.println(forest);
			//System.out.println(content);
			//System.out.println(outTable.toString());
			//System.out.println(retStr);
		}
		return outStr;
	}

	private static String  getValue(JSONArray inData, JSONObject inS, String rKey, int rIndex, Map keys)
	{
		try
		{
			JSONObject dataItem = null;
			for(int i=0;i<inData.length();i++)
			{
				String attKey = inS.getString("id");
				String dataKey = inData.getJSONObject(i).getJSONObject("attribute").getString("id");

				if(dataKey.equals("sum"))
				{
					dataKey += inData.getJSONObject(i).getJSONObject("attribute").getJSONObject("params").getJSONObject("attribute").getString("id");

				}
				if(attKey.equals("sum"))
				{
					attKey += inS.getJSONObject("params").getJSONObject("attribute").getString("id");
				}

				if(attKey.equals(dataKey)) dataItem=inData.getJSONObject(i);
			}
			JSONArray valArr = null;
	        String retVal = "";

			if(dataItem!=null){

	           valArr = dataItem.getJSONArray("values");
	           if(rIndex < valArr.length())
	           {

	        	   //apply the indentation....
	        	   if(inS.getString("id").equals("summary"))
	        	   {
		        	   retVal= valArr.getString(rIndex);
		        	   retVal = retVal.replaceAll("(<([^>]+)>)","");

	        		   Map myKey = (Map) keys.get(rKey);
	        		   for(int i=0;i<Integer.valueOf(myKey.get("depth").toString());i++) retVal="&nbsp;&nbsp;&nbsp;&nbsp;" + retVal;
	        	   }
	        	   else if(inS.getString("id").equals("progress"))
	        	   {
		        	   double retDbl= valArr.getDouble(rIndex);

	        		   if(retDbl==0)
	        		   {
	        			   retVal = "%0.0";
	        		   }
	        		   else
	        		   {
	        			   //double dv = Double.valueOf(retVal).doubleValue();
	        			   retDbl=retDbl*100;
	        			   BigDecimal bd = new BigDecimal(retDbl);
	        			   bd = bd.setScale(2, RoundingMode.HALF_UP);
	        			   retVal = "%"+String.valueOf(bd.doubleValue());
	        		   }
	        	   }
	        	   else if(inS.getString("id").equals("done"))
	        	   {
		        	   boolean  retBool= valArr.getBoolean(rIndex);
		        	   retVal = String.valueOf(retBool);
	        	   }
	        	   else
	        	   {
		        	   retVal= valArr.getString(rIndex);
		        	   retVal = retVal.replaceAll("(<([^>]+)>)","");
	        	   }

	        	   return retVal;
	           }
	        }
           return " ";

		}
		catch(Exception e)
		{
			return " ";
		}
   }

}

