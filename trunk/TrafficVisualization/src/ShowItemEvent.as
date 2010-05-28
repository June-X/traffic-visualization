/*
* Used to pass data when hiding or showing a device type.
*/

package 
{
	
	public class ShowItemEvent
	{
		// Event type.
		public static const SHOW_DEVICE_TYPE:String = "showItemType";
		
		// Type of device. This should match a type value from Device.
		public var itemType:String;
		// Specifies whether or not to show a type of device.
		public var show:Boolean;
		
		function ShowItemEvent(itemType:String, show:Boolean)
		{
			this.deviceType = deviceType;
			this.show = show;
		}
	}
}