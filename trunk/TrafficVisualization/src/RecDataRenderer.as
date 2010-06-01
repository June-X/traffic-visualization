package
{
	import flash.display.Graphics;
	import flash.geom.Rectangle;
	import mx.charts.ChartItem;
	import mx.charts.chartClasses.GraphicsUtilities;
	import mx.core.IDataRenderer;
	import mx.graphics.IFill;
	import mx.graphics.IStroke;
	import mx.skins.ProgrammaticSkin;
	import mx.controls.Label;
	import mx.core.UIComponent;
	import mx.charts.PlotChart;
	import mx.charts.series.items.PlotSeriesItem;
	
	public class RecDataRenderer extends UIComponent implements IDataRenderer
	{
		private var _label:Label;
		
		public function RecDataRenderer():void
		{
			super();
			_label = new Label();
			addChild(_label);
			_label.setStyle("color",0xFFFFFF);        
		}
		private var _chartItem:ChartItem;
		
		public function get data():Object
		{
			return _chartItem;
		}
		
		public function set data(value:Object):void
		{
			if (_chartItem == value)
				return;
			_chartItem = ChartItem(value);
			
			if(_chartItem != null)
				_label.text = PlotSeriesItem(_chartItem).xValue.toString();
		}
		
		private static const fills:Array = [0xFF0000,0x00FF00,0x0000FF,
			0x00FFFF,0xFF00FF,0xFFFF00,
			0xAAFFAA,0xFFAAAA,0xAAAAFF];     
		override protected function updateDisplayList(unscaledWidth:Number,
													  unscaledHeight:Number):void
		{
			super.updateDisplayList(unscaledWidth, unscaledHeight);
			
			var fill:Number = 0;
			
			
			var rc:Rectangle = new Rectangle(0, 0, width , height );
			
			var g:Graphics = graphics;
			g.clear();
			g.moveTo(rc.left,rc.top);
			g.beginFill(fill);
			g.lineTo(rc.right,rc.top);
			g.lineTo(rc.right,rc.bottom);
			g.lineTo(rc.left,rc.bottom);
			g.lineTo(rc.left,rc.top);
			g.endFill();
			
			_label.setActualSize((_label.getExplicitOrMeasuredWidth()* 1000),(_label.getExplicitOrMeasuredHeight()*1000));
			_label.move(unscaledWidth - _label.getExplicitOrMeasuredWidth(),
				unscaledHeight/2 - _label.getExplicitOrMeasuredHeight()/2);
		}
		
	}
}	
