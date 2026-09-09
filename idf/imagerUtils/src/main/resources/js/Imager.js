jQuery(function ($) {
    var imagerMacroInit = function ()
    {
        $(".imagerSettingsDiv").each(function()
        {
        var imagerSettings = $(this).find("input.imagerSettings").val();
        var json;
        // determine if the browser has native JSON parser support & create JSON object
        if (typeof (JSON) !== 'undefined' && typeof (JSON.parse) === 'function')
        {
            json = JSON.parse(decodeURIComponent(imagerSettings).replace(/\+/g, '\u00a0'));
        } else {
            json = eval('(' + decodeURIComponent(imagerSettings).replace(/\+/g, '\u00a0') + ')');
        }

        // create table
        var html = "<table border=\"1\"><tr><th>DAY</th><th>DATE</th></tr>";
        for (var i=0; i<7; i++)
        {
            html = html + "<tr><td>" + json.imagerSettings[i].day + "</td><td>" + json.imagerSettings[i].date + "</td></tr>";
        }
        html = html + "</table>";
        //$(this).html(JSON.stringify(json,0,4));
        $(this).html(html);
    });
};
$(document).ready(function()
    {
        imagerMacroInit();
    });
});