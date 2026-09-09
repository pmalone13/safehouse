package com.idealfed.pageimager.rest;

import javax.xml.bind.annotation.*;
@XmlRootElement(name = "admin")
@XmlAccessorType(XmlAccessType.FIELD)
public class UtilsModel {

    @XmlAttribute
    private String id;

    @XmlElement(name = "config")
    private String config;

    public UtilsModel() {
    }

	public UtilsModel(String id, String config) {
	   this.id = id;
	   this.config = config;
	}

    public String getConfig() {
        return config;
    }

    public void setConfig(String config) {
        this.config = config;
    }

	public String getId() {
	   return id;
	}

	public void setId(String id) {
	   this.id = id;
	}

    public String serialize()
    {
		return "{\"id\":\"" + id + "\",\"config\":\"" + config +"\"}";
	}
}