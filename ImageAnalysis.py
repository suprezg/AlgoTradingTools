import matplotlib
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
import mplfinance as mpf
import matplotlib.pyplot as plt
from ultralyticsplus import YOLO, render_result

from DataManagement import StockScraper

matplotlib.use('Agg')

class MovementClassifier:

    def __init__(self, ticker, interval, api):
        try:
            obj = StockScraper(ticker = ticker, interval = interval, api = api)
            self.df = obj.getData()
            self.img = np.nan
            self.model = np.nan
            self.content = np.nan
            self._prepareData()
        except Exception as e:
            raise Exception("Error initializing MovementClassifier") from e
    
    def _prepareData(self):
        try:
            self.df = pd.DataFrame(self.df)
            self.df.dropna(inplace = True)
            self.df = self.df.rename_axis('Date')
            self.df = self.df.iloc[-150:]
        except Exception as e:
            raise Exception("Error preparing data for MovementClassifier") from e
    
    def train(self):
        try:
            self.model = YOLO('foduucom/stockmarket-future-prediction')
            self.model.overrides['conf'] = 0.25
            self.model.overrides['iou'] = 0.45
            self.model.overrides['agnostic_nms'] = False
            self.model.overrides['max_det'] = 1000 
            fig, ax = mpf.plot(self.df, type="candle", style="yahoo", title=f"", axisoff=True, ylabel="", 
                               ylabel_lower="", volume=False, figsize=(18, 6.5), returnfig=True)
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
            buffer.seek(0)
            self.img = Image.open(buffer).convert('RGB')
        except Exception as e:
            raise Exception("Error training MovementClassifier model") from e

    
    def classify(self):
        try:
            if self.model is None or self.img is None:
                raise Exception("Model not trained or image not generated")
            results = self.model.predict(self.img)
            render = render_result(model=self.model, image=self.img, result=results[0])
            img_byte_array = BytesIO()
            render.save(img_byte_array, format='PNG')
            img_byte_array.seek(0)
            self.content = img_byte_array.getvalue()
        except Exception as e:
            raise Exception("Error classifying movement using MovementClassifier") from e

    def getContent(self):
        try:
            if self.content is None:
                raise Exception("No content generated. Ensure classify() has been called successfully.")
            return self.content
        except Exception as e:
            raise Exception("Error retrieving content from MovementClassifier") from e


class PatternClassifier:

    def __init__(self, ticker, interval, api):
        try:
            obj = StockScraper(ticker = ticker, interval = interval, api = api)
            self.df = obj.getData()
            self.img = np.nan
            self.model = np.nan
            self.content = np.nan
            self._prepareData()
        except Exception as e:
            raise Exception("Error initializing PatternClassifier") from e
    
    def _prepareData(self):
        try:
            self.df = pd.DataFrame(self.df)
            self.df.dropna(inplace = True)
            self.df = self.df.rename_axis('Date')
            self.df = self.df.iloc[-150:]
        except Exception as e:
            raise Exception("Error preparing data for PatternClassifier") from e
    
    def train(self):
        try:
            self.model = YOLO('foduucom/stockmarket-pattern-detection-yolov8')
            self.model.overrides['conf'] = 0.25
            self.model.overrides['iou'] = 0.45
            self.model.overrides['agnostic_nms'] = False
            self.model.overrides['max_det'] = 1000 
            fig, ax = mpf.plot(self.df, type="candle", style="yahoo", title=f"", axisoff=True, ylabel="", 
                               ylabel_lower="", volume=False, figsize=(18, 6.5), returnfig=True)
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
            buffer.seek(0)
            self.img = Image.open(buffer).convert('RGB')
        except Exception as e:
            raise Exception("Error training PatternClassifier model") from e
    
    def classify(self):
        try:
            if self.model is None or self.img is None:
                raise Exception("Model not trained or image not generated")
            results = self.model.predict(self.img)
            render = render_result(model=self.model, image=self.img, result=results[0])
            img_byte_array = BytesIO()
            render.save(img_byte_array, format='PNG')
            img_byte_array.seek(0)
            self.content = img_byte_array.getvalue()
        except Exception as e:
            raise Exception("Error classifying pattern using PatternClassifier") from e

    def getContent(self):
        try:
            if self.content is None:
                raise Exception("No content generated. Ensure classify() has been called successfully.")
            return self.content
        except Exception as e:
            raise Exception("Error retrieving content from PatternClassifier") from e
