    var imagerMacroInit = function ()
    {

        imagerMacroInitExt();
	    try
	    {
	       var imagerSettings = imagerMacroGetSettings();
		}
		catch(e)
		{
			Ext.Msg.alert("Info","Error acquiring settings for macro")
			return
		}

		if(imagerSettings.id==0)
		{
			Ext.Msg.alert("Info","No settings for macro");
			return;
		}
        var sRows = JSON.parse(imagerSettings.config);
        imagerMacroLoadPageGrid(sRows);

    };

    var imagerMacroReloadData = function ()
    {
	    try
	    {
	       var imagerSettings = imagerMacroGetSettings();
		}
		catch(e)
		{
			Ext.Msg.alert("Info","Error acquiring settings for macro")
			return
		}
		if(imagerSettings.id==0)
		{
			Ext.Msg.alert("Info","No settings for macro");
			return;
		}

        var sRows = JSON.parse(imagerSettings.config);
        imagerMacroLoadPageGrid(sRows);
    };

    var  imagerMacroGetSettings = function ()
    {
		var retData = null;
		jQuery.ajax({
			async: false,
			type: 'GET',
		    contentType: 'application/json',
			url: '/rest/utils/1.0/message/' + Confluence.getContentId(),
			timeout: 60000,
			success: function(data) {
				retData = data;
			},
			error: function(e) {
				if(e.responseText)
				{
					retData = "Failed issue get: " + e.responseText;
				}
				else
				{
					retData = "Failed issue get: " + e.message;
				}
			}
		});
		return retData;
    };

    var  imagerMacroPostSettings = function (inSettings)
    {
		var retData = null;
		var outConfig = {"id":Confluence.getContentId(),"config":JSON.stringify(inSettings)};
		jQuery.ajax({
			async: false,
			type: 'POST',
		    contentType: 'application/json',
			url: '/rest/utils/1.0/message/update',
			data: JSON.stringify(outConfig),
			timeout: 60000,
			success: function(data) {
				retData = true;
			},
			error: function(e) {
				retData=false;
				if(e.responseText=="OK")
				{
				    retData=true;
				}
				else
				{
                    if(e.responseText)
                    {
                        console.log(e.responseText)
                    }
                    else
                    {
                        console.log(e.message)
                    }
				}
			}
		});
		imagerMacroCommitSave();
		return retData;
    };






//******************************bus logic here

var imagerMacroCopyPage = function(sourcePageId, targetPageId, macroPageId)
{

    var retData = null;
		jQuery.ajax({
			async: false,
			type: 'GET',
		    contentType: 'application/json',
			url: '/rest/utils/1.0/message/copypage?targetPageId='+targetPageId+'&sourcePageId='+sourcePageId+'&macroPageId='+macroPageId,
			timeout: 60000,
			success: function(data) {
				retData = data;
			},
			error: function(e) {
				if(e.responseText)
				{
					retData = "Failed issue get: " + e.responseText;
				}
				else
				{
					retData = "Failed issue get: " + e.message;
				}
			}
		});
		if(typeof retData=="string")
		{
			Ext.Msg.alert("Error","Error performing page copy")
			return;
		}
		return retData;
}




jQuery(function ($) {
    $(document).ready(function()
    {
        imagerMacroInit();
    });
});