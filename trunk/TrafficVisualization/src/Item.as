package 
{
	[RemoteClass(alias="vo.item")]
	public class Item
	{
		public static const TYPE_URL:String = "URL";
		public static const TYPE_KeyBoard:String = "keyboard";
		public static const TYPE_Mouse:String = "mouse";
		
		public var id:String;                    // item id.
		public var name:String;                    // item name.
		public var type:String;                    // item type
		// Valid values are url, keyboard, and mouse.
		public var url:String;                    // url visited
		public var keyboard:String;                // keyboard input
		public var mouse:String;                   //url of mouse click
		public var x:Number;                    // Used only for the network topology view.
		public var y:Number;                    // Used only for the network topology view.
		public var connections:Array;            // Array of id strings.
	}
}