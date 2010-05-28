/*
 * Data User to store URL and User Input data
 * 
 */

package vo;

public class item
{
      private String id;                                     //item id
      private String name;                                   //item name
      private String type;                                   //item type, valid values are icon, URL, keyboard, and mouse
      
      private String url;                                    //url data
      private String keyboard;                               //keyboard input data
      private String mouse;                                  //mouse click data
      private int x;
      private int y;
      private String[] connections;
      
      public void setId(String s)
      {
    	  id = s;
      }
      
      public String getId()
  	{
  		return id;
  	}
  	
  	public void setName(String n)
  	{
  		name = n;
  	}
  	
  	public String getName()
  	{
  		return name;
  	}

  	public void setType(String t)
  	{
  		type = t;
  	}
  	
  	public String getType()
  	{
  		return type;
  	}
  	
  	public void setUrl(String i)
	{
		url = i;
	}
	
	public String getUrl()
	{
		return url;
	}
	
	public void setKey(String i)
	{
		keyboard = i;
	}

	public String getKey()
	{
		return keyboard;
	}
	
	public void setMouse(String i)
	{
		mouse = i;
	}

	public String getMouse()
	{
		return mouse;
	}
	
	public void setX(int i)
	{
		x = i;
	}

	public int getX()
	{
		return x;
	}

	public void setY(int i)
	{
		y = i;
	}

	public int getY()
	{
		return y;
	}
	
	public void setConnections(String[] c)
	{
		connections = c;
	}
	
	public String[] getConnections()
	{
		return connections;
	}
}