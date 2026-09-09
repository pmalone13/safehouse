package com.idealfed.pageimager.rest;

import com.atlassian.plugins.rest.common.security.AnonymousAllowed;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.inject.Inject;

import com.atlassian.confluence.util.GeneralUtil;
import com.atlassian.sal.api.pluginsettings.PluginSettings;
import com.atlassian.sal.api.pluginsettings.PluginSettingsFactory;
import com.atlassian.sal.api.transaction.TransactionCallback;
import com.atlassian.sal.api.transaction.TransactionTemplate;
import com.atlassian.confluence.pages.PageManager;
import com.atlassian.confluence.pages.Page;
import com.atlassian.confluence.spaces.SpaceManager;
import com.atlassian.confluence.core.DefaultSaveContext;
import com.atlassian.plugin.spring.scanner.annotation.component.Scanned;
import com.atlassian.plugin.spring.scanner.annotation.imports.ComponentImport;

/**
 * A resource of message.
 */
@Path("/message")
@Scanned
public class Utils {

  @ComponentImport
  private final PageManager pageManager;
  @ComponentImport
  private final SpaceManager spaceManager;
    @ComponentImport
    private final PluginSettingsFactory pluginSettingsFactory;
    private PluginSettings pluginSettings;

    @Inject
    public Utils(PluginSettingsFactory pluginSettingsFactory, PageManager pageManager, SpaceManager spaceManager)
    {
        this.pluginSettingsFactory = pluginSettingsFactory;
        this.pageManager = pageManager;
        this.spaceManager = spaceManager;
    }


    @GET
    @AnonymousAllowed
    @Produces({MediaType.APPLICATION_JSON})
	public Response getMessage(@QueryParam("key") String key)
	{
	   if(key!=null)
	   {
	   	    pluginSettings = pluginSettingsFactory.createGlobalSettings();
	        String retS = (String) pluginSettings.get("pageimager_" + key);
	        if(retS==null)
	        {
			  return Response.ok(new UtilsModel("0","No Data")).build();
			}
			else
			{
			  return Response.ok(new UtilsModel(key,retS)).build();
			}
	   }
	   else
	   {
		  return Response.ok(new UtilsModel("0","No Key")).build();
	   }
	}

	@GET
	@AnonymousAllowed
	@Produces({MediaType.APPLICATION_JSON})
	@Path("/{key}")
	public Response getMessageFromPath(@PathParam("key") String key)
	{
	   if(key!=null)
	   {
	   	    pluginSettings = pluginSettingsFactory.createGlobalSettings();
	        String retS = (String) pluginSettings.get("pageimager_" + key);
	        if(retS==null)
	        {
			  return Response.ok(new UtilsModel("0","No Data")).build();
			}
			else
			{

			  return Response.ok(new UtilsModel(key,retS)).build();
			}
	   }
	   else
	   {
		  return Response.ok(new UtilsModel("0","No Key")).build();
	   }
	}



    @GET
    @AnonymousAllowed
    @Produces({MediaType.APPLICATION_JSON})
    @Path("/copypage")
	public Response getMessage(@QueryParam("targetPageId") String targetPageId,@QueryParam("sourcePageId") String sourcePageId,@QueryParam("macroPageId") String macroPageId)
	{
	   if(macroPageId==null) return Response.ok(new UtilsModel("0","No root page")).build();

	   if(sourcePageId!=null)
	   {
		  long sPageId = Long.parseLong(sourcePageId);
		  long mPageId = Long.parseLong(macroPageId);

		  Page sPage =  this.pageManager.getPage(sPageId);

          //special handling for new page...
          if(targetPageId.equals("initialize"))
	      {
    		  Page mPage =  this.pageManager.getPage(mPageId);
			  targetPageId = "New Page";
			  //must create a new page under acroPage
  			  Page page = new Page();
 			  page.setTitle(sPage.getTitle()+ " - PSR Report");
			  page.setParentPage(mPage);
			  page.setBodyAsString(sPage.getBodyAsString());
			  page.setVersion(1);
			  page.setSpace(mPage.getSpace());

			  mPage.addChild(page);

			  //page.setCreatorName("Auto-Created");
			  this.pageManager.saveContentEntity(page, null);
			  this.pageManager.saveContentEntity(mPage, null);
	      }
	      else
	      {
			  long tPageId = Long.parseLong(targetPageId);
			  Page tPage =  this.pageManager.getPage(tPageId);
			  Page tOrigPage = (Page) tPage.clone();
			  tPage.setBodyAsString(sPage.getBodyAsString());
			  this.pageManager.saveContentEntity(tPage,tOrigPage, DefaultSaveContext.DEFAULT);
		  }
  	      return Response.ok(new UtilsModel("0",sourcePageId + " -> " + targetPageId)).build();
	   }
	   else
	   {
		  return Response.ok(new UtilsModel("0","No Parameters")).build();
	   }
	}

/*
else if(targetPageId.equals("1867823"))
		  {
			  Page mPage =  this.pageManager.getPage(mPageId);
			  long tPageId = Long.parseLong(targetPageId);
			  Page tPage =  this.pageManager.getPage(tPageId);

			  tPage.setSpace(mPage.getSpace());

			  mPage.addChild(tPage);

			  //page.setCreatorName("Auto-Created");
			  this.pageManager.saveContentEntity(tPage, null);
			  this.pageManager.saveContentEntity(mPage, null);
	      }
*/


    @POST
    @Path("/update")
    @AnonymousAllowed
    @Consumes(MediaType.APPLICATION_JSON)
	@Produces(MediaType.APPLICATION_JSON)
    public Response postStrMsg(UtilsModel cfg) {

	    pluginSettings = pluginSettingsFactory.createGlobalSettings();
	    pluginSettings.put("pageimager_" + cfg.getId(), cfg.getConfig());

        return Response.status(200).entity("OK").build();
    }


    @DELETE
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
	@Produces({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
    public Response deleteMsg(@FormParam("pageid") String id) {
        String output = "DELETE:Jersey say : " + id;
        return Response.status(200).entity(output).build();
    }

}