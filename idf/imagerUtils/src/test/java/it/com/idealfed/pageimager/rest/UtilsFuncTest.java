package it.com.idealfed.pageimager.rest;

import org.junit.Test;
import org.junit.After;
import org.junit.Before;
import org.mockito.Mockito;
import static org.junit.Assert.*;
import static org.mockito.Mockito.*;
import com.idealfed.pageimager.rest.Utils;
import com.idealfed.pageimager.rest.UtilsModel;
import org.apache.wink.client.Resource;
import org.apache.wink.client.RestClient;

public class UtilsFuncTest {

    @Before
    public void setup() {

    }

    @After
    public void tearDown() {

    }

    @Test
    public void messageIsValid() {

        String baseUrl = System.getProperty("baseurl");
        String resourceUrl = baseUrl + "/rest/utils/1.0/message";

        RestClient client = new RestClient();
        Resource resource = client.resource(resourceUrl);

        UtilsModel message = resource.get(UtilsModel.class);

        assertEquals("wrong message","Hello World",message.getMessage());
    }
}
