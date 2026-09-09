package com.idealfed.pageimager;

import java.util.Map;
import java.util.List;

import com.atlassian.confluence.content.render.xhtml.ConversionContext;
import com.atlassian.confluence.macro.Macro;
import com.atlassian.confluence.macro.MacroExecutionException;
import com.atlassian.confluence.pages.PageManager;
import com.atlassian.confluence.pages.Page;
import com.atlassian.confluence.spaces.SpaceManager;
import com.atlassian.confluence.util.GeneralUtil;
import com.atlassian.confluence.user.AuthenticatedUserThreadLocal;
import com.atlassian.user.User;
import com.opensymphony.util.TextUtils;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import com.atlassian.confluence.json.json.JsonArray;
import com.atlassian.confluence.json.json.JsonObject;
import com.atlassian.confluence.renderer.radeox.macros.MacroUtils;
import com.atlassian.confluence.util.GeneralUtil;
import com.atlassian.confluence.util.velocity.VelocityUtils;
import org.apache.velocity.VelocityContext;
import com.atlassian.plugin.spring.scanner.annotation.component.Scanned;
import com.atlassian.plugin.spring.scanner.annotation.imports.ComponentImport;
import org.springframework.beans.factory.annotation.Autowired;

@Scanned
public class ImagerMacro implements Macro
{
  @ComponentImport
  private final PageManager pageManager;
  @ComponentImport
  private final SpaceManager spaceManager;

  @Autowired
  public ImagerMacro(PageManager pageManager, SpaceManager spaceManager)
  {
    this.pageManager = pageManager;
    this.spaceManager = spaceManager;
  }


  DateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy");
  DateFormat dayFormat = new SimpleDateFormat("EEEE");


  @Override
  public BodyType getBodyType()
  {
    return BodyType.NONE;
  }

  @Override
  public OutputType getOutputType()
  {
    return OutputType.BLOCK;
  }

  @Override
  public String execute(Map<String, String> params, String body, ConversionContext conversionContext)
                                                                       throws MacroExecutionException
  {
    Date startDate = getStartDateFromParams(params);
    JsonObject dayDateJsonObject = new JsonObject();
    JsonArray dayDateJsonArray = new JsonArray();

    for (int i=0; i < 7; i++)
    {
      Calendar cal = Calendar.getInstance();
      cal.setTime(startDate);
      cal.add(Calendar.DATE, i );
      Date date = cal.getTime();
      String day = dayFormat.format(date);
      dayDateJsonArray.add(nextDayDateJsonObject(day, date));
    }

    dayDateJsonObject.setProperty("imagerSettings", dayDateJsonArray);

    Map context = MacroUtils.defaultVelocityContext();
    //context.put("imagerSettings", GeneralUtil.urlEncode(dayDateJsonObject.serialize()));
    context.put("imagerSettings", "na");
    return VelocityUtils.getRenderedTemplate("imagermacro.vm", context);

  }

  private Date getStartDateFromParams(Map params) throws MacroExecutionException
  {
    Date startDate = new Date();
    if (params.size() > 1)
    {
      try
      {
      startDate = dateFormat.parse((String) params.get("date"));
      }
      catch (ParseException e)
      {
        throw new MacroExecutionException("Unable to parse date");
      }
    }
    return startDate;
  }

  private JsonObject nextDayDateJsonObject(String day, Date date)
  {
    JsonObject nextDayDateJsonObject = new JsonObject();
    nextDayDateJsonObject.setProperty("date",date);
    nextDayDateJsonObject.setProperty("day", day);
    return nextDayDateJsonObject;
  }
}