from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
#from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.detection import DownsampleLogDetectorFactory
from fiji.plugin.trackmate.tracking.oldlap import LAPTrackerFactory
from fiji.plugin.trackmate.detection import DetectorKeys #pr
#from fiji.plugin.trackmate.tracking.sparselap import SparseLAPTrackerFactory
from fiji.plugin.trackmate.tracking import LAPUtils
from fiji.plugin.trackmate.action import ExportStatsToIJAction
from fiji.plugin.trackmate.action import TrackBranchAnalysis
#from fiji.plugin.trackmate import Spot
#from fiji.plugin.trackmate import Spot
from ij.plugin import HyperStackConverter
from ij.measure import ResultsTable
from ij import IJ
from ij import WindowManager
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
import sys
import fiji.plugin.trackmate.features.track.TrackDurationAnalyzer as TrackDurationAnalyzer
from fiji.plugin.trackmate.graph import GraphUtils

from java.io import File
from fiji.plugin.trackmate.io import TmXmlWriter
    
# Get currently selected image
#imp = WindowManager.getCurrentImage()
#imp = IJ.openImage('D:\\syncplicity\\z003prfz\\Projects\\MA\\test\\eli-new-unsync-bf-47\\out-focus\\merged\\merged.tif')
imp = IJ.openImage('D:\\MA\\test\\eli-new-unsync-bf-47\\out-focus\\before\\out\\stacks\\before_corrected_womask_substracted_bradjust.tif')

impconv = HyperStackConverter()
imp = impconv.toHyperStack(imp, 1, 1, imp.getStackSize())

imp.show()
#print(imp.getZ())
#print(imp.getT())
#print(imp.getC())
print(imp.getStackSize())

#----------------------------
# Create the model object now
#----------------------------
    
# Some of the parameters we configure below need to have
# a reference to the model at creation. So we create an
# empty model now.
    
model = Model()
    
# Send all messages to ImageJ log window.
model.setLogger(Logger.IJ_LOGGER)

#------------------------
# Prepare settings object
#------------------------
       
settings = Settings()
settings.setFrom(imp)
       
# Configure detector - We use the Strings for the keys
#settings.detectorFactory = LogDetectorFactory()
settings.detectorFactory = DownsampleLogDetectorFactory()
settings.detectorSettings = {
	DetectorKeys.KEY_RADIUS: 14.,
	DetectorKeys.KEY_DOWNSAMPLE_FACTOR: 4,
	DetectorKeys.KEY_THRESHOLD : 0.,
}
print(settings.detectorSettings) 

# Config initial spot filters value
settings.initialSpotFilterValue = 3

# Configure spot filters - Classical filter on quality
#filter1 = FeatureFilter('QUALITY', 2.3, True)
#settings.addSpotFilter(filter1)

# Configure tracker - We want to allow merges and fusions
#settings.trackerFactory = SparseLAPTrackerFactory()
settings.trackerFactory = LAPTrackerFactory()
settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap() # almost good enough
print(LAPUtils.getDefaultLAPSettingsMap())
settings.trackerSettings['LINKING_MAX_DISTANCE'] = 15.0
settings.trackerSettings['LINKING_FEATURE_PENALTIES'] = {}
#gap closing
settings.trackerSettings['ALLOW_GAP_CLOSING'] = True
settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 15.0
settings.trackerSettings['MAX_FRAME_GAP'] = 5
settings.trackerSettings['GAP_CLOSING_FEATURE_PENALTIES'] = {}
#splitting
settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = True
settings.trackerSettings['SPLITTING_MAX_DISTANCE'] = 15.0
settings.trackerSettings['SPLITTING_FEATURE_PENALTIES'] = {}
#merging
settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
settings.trackerSettings['MERGING_MAX_DISTANCE'] = 15.0
settings.trackerSettings['MERGING_FEATURE_PENALTIES'] = {}
#etc
#settings.trackerSettings['ALTERNATIVE_LINKING_COST_FACTOR'] = 1.05
#settings.trackerSettings['BLOCKING_VALUE'] = Infinity
#settings.trackerSettings['CUTOFF_PERCENTILE'] = 0.9			

# Configure track analyzers - Later on we want to filter out tracks 
# based on their displacement, so we need to state that we want 
# track displacement to be calculated. By default, out of the GUI, 
# not features are calculated. 
    
# The displacement feature is provided by the TrackDurationAnalyzer.
    
settings.addTrackAnalyzer(TrackDurationAnalyzer())

# Configure track filters - We want to get rid of the two immobile spots at 
# the bottom right of the image. Track displacement must be above 10 pixels.
    
#filter2 = FeatureFilter('TRACK_DISPLACEMENT', 10, True)
#settings.addTrackFilter(filter2)

#print(settings.getSpotFilter())
#print(settings.getTrackFilter())
    
#-------------------
# Instantiate plugin
#-------------------
    
trackmate = TrackMate(model, settings)
       
#--------
# Process
#--------
    
ok = trackmate.checkInput()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))
    
ok = trackmate.process()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))
    
       
#----------------
# Display results
#----------------
     
selectionModel = SelectionModel(model)
displayer =  HyperStackDisplayer(model, selectionModel, imp)
displayer.render()
displayer.refresh()
    
# Echo results with the logger we set at start:
model.getLogger().log(str(model))

# export needed files for further analysis

outfile = TmXmlWriter(File('D:\\MA\\test\\eli-new-unsync-bf-47\\model.xml'))
outfile.appendModel(model)
outfile.writeToFile()

# show dialog windows
esta = ExportStatsToIJAction()
esta.execute(trackmate)

tba = TrackBranchAnalysis(selectionModel)
tba.execute(trackmate)

print(WindowManager.getNonImageTitles())

# echo feature model

print(trackmate.getModel().getTrackModel().echo())

# print pretty string track model

print("#" * 20)
print(model.toString())

print("#" * 20)
print(GraphUtils.toString(trackmate.getModel().getTrackModel()) + "A")

print("#" * 20)
print(model.getTrackModel().echo())

#print(model.getFeatureModel().echo())
#tm = trackmate.getModel().getTrackModel()
#print(tm)
#st = GraphUtils.toString(st)
#print(GraphUtils.toString(st))

#test 
#mdl = trackmate.getModel()
#fm = mdl.getFeatureModel()

#trackIDs = mdl.getTrackModel().trackIDs(True)
#spotFeatures = trackmate.getModel().getFeatureModel().getSpotFeatures()

#spotTable = ResultsTable()

##spot = Spot()
##print([spot.frameComparator(i) for i in trackIDs])


#print(vars(Spot))
#for trackID in trackIDs:
#	track = mdl.getTrackModel().trackSpots(trackID);
#	track = list(track)
#	track = sorted(track, frameComparator)
#	print(track)
#	print('##' * 10)