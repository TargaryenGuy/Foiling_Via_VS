// Simcenter STAR-CCM+ macro: Foiling_Macro_Part_2.java (Combined Full Macro)
// Written by Simcenter STAR-CCM+ 18.04.008

package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;
import star.meshing.*;
import star.resurfacer.*;

public class Foiling_Macro_Part_2 extends StarMacro {

  public void execute() {
    execute0();
  }

  private void execute0() {

    Simulation simulation_0 = 
      getActiveSimulation();

    MeshPartFactory meshPartFactory_0 = 
      simulation_0.get(MeshPartFactory.class);

    MeshPart meshPart_11 = 
      ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Glass"));

    PartSurface partSurface_0 = 
      ((PartSurface) meshPart_11.getPartSurfaceManager().getPartSurface("Bottom_Surface_I"));

    PartSurface partSurface_1 = 
      ((PartSurface) meshPart_11.getPartSurfaceManager().getPartSurface("Bottom_Surface_II"));

    meshPartFactory_0.newPartFromPartSurfaces(new NeoObjectVector(new Object[] {partSurface_0, partSurface_1}));

    MeshPart meshPart_22 = 
      ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Seals"));

    MeshPart meshPart_33 = 
      ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Part"));

    meshPartFactory_0.combineMeshParts(meshPart_22, new NeoObjectVector(new Object[] {meshPart_33}));

/////////////What lenghth of Area source you want 25mm/50mm/75mm put it as below //////////////

    double AS_length = 25.0f;
    
/////////////What distance you want to move the surface away from the sealsr put it as below //////////////

    double Translation_length = 0.003f;

    // Start Surface Mesh Widget for Geometry
    PartRepresentation partRepresentation_0 = 
      (PartRepresentation) simulation_0.getRepresentationManager().getObject("Geometry");

    PartSurfaceMeshWidget partSurfaceMeshWidget_4 = partRepresentation_0.startSurfaceMeshWidget();

    MeshPart meshPart_2 = 
    (MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Seals");

    MeshPart meshPart_0 = 
    (MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Glass");

    RootDescriptionSource rootDescriptionSource_0 = 
      simulation_0.get(SimulationMeshPartDescriptionSourceManager.class).getRootDescriptionSource();

    partSurfaceMeshWidget_4.setActiveParts(new NeoObjectVector(new Object[] {meshPart_2, meshPart_0}), rootDescriptionSource_0);
    partSurfaceMeshWidget_4.startSurfaceRepairControllers();

    SurfaceMeshWidgetDisplayController surfaceMeshWidgetDisplayController_4 = 
      partSurfaceMeshWidget_4.getControllers().getController(SurfaceMeshWidgetDisplayController.class);
    surfaceMeshWidgetDisplayController_4.hideAllFaces();
    surfaceMeshWidgetDisplayController_4.showAllFaces();

SurfaceMeshWidgetSelectController surfaceMeshWidgetSelectController_2 = 
  partSurfaceMeshWidget_4.getControllers().getController(SurfaceMeshWidgetSelectController.class);

SurfaceMeshWidgetRepairController surfaceMeshWidgetRepairController_2 = 
  partSurfaceMeshWidget_4.getControllers().getController(SurfaceMeshWidgetRepairController.class);

LabCoordinateSystem labCoordinateSystem_0 = simulation_0.getCoordinateSystemManager().getLabCoordinateSystem();

SurfaceMeshWidgetDiagnosticsController surfaceMeshWidgetDiagnosticsController_2 = 
  partSurfaceMeshWidget_4.getControllers().getController(SurfaceMeshWidgetDiagnosticsController.class);

    // Translation of each surface///
    //User need to give direction vector of translation accrording to the geometry's co-ordinate system and orientaion///////////////////////////////////////
    translateSurface(meshPart_2, "Left_Surface", surfaceMeshWidgetSelectController_2, surfaceMeshWidgetRepairController_2, labCoordinateSystem_0, Translation_length, new double[] {0.0, -1.0, 0.0});
    translateSurface(meshPart_2, "Right_Surface", surfaceMeshWidgetSelectController_2, surfaceMeshWidgetRepairController_2, labCoordinateSystem_0, Translation_length, new double[] {0.0, 1.0, 0.0});
    //translateSurface(meshPart_2, "Bottom_Surface_I", surfaceMeshWidgetSelectController_2, surfaceMeshWidgetRepairController_2, labCoordinateSystem_0, Translation_length, new double[] {0.0, 0.0, 0.0});
    //translateSurface(meshPart_2, "Bottom_Surface_II", surfaceMeshWidgetSelectController_2, surfaceMeshWidgetRepairController_2, labCoordinateSystem_0, Translation_length, new double[] {0.0, 0.0, 0.0});

    partSurfaceMeshWidget_4.stop();

    // Create New Part From Surfaces
    //MeshPartFactory meshPartFactory_0 = simulation_0.get(MeshPartFactory.class);
    PartSurface[] surfaces = {
        meshPart_2.getPartSurfaceManager().getPartSurface("Left_Surface"),
        meshPart_2.getPartSurfaceManager().getPartSurface("Bottom_Surface_I"),
        meshPart_2.getPartSurfaceManager().getPartSurface("Right_Surface"),
        meshPart_2.getPartSurfaceManager().getPartSurface("Bottom_Surface_II")
    };
    //meshPartFactory_0.newPartFromPartSurfaces(new NeoObjectVector(Arrays.asList(surfaces)));
    meshPartFactory_0.newPartFromPartSurfaces(new NeoObjectVector(surfaces));

    MeshPart guideCurvePart = (MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Part");
    guideCurvePart.setPresentationName("Guide_Curve");

    // Meshing
    AutoMeshOperation autoMeshOperation = simulation_0.get(MeshOperationManager.class)
        .createAutoMeshOperation(new StringVector(new String[] { "star.resurfacer.ResurfacerAutoMesher" }),
            new NeoObjectVector(new Object[] { guideCurvePart }));

    ResurfacerAutoMesher resurfacerMesher = 
        (ResurfacerAutoMesher) autoMeshOperation.getMeshers().getObject("Surface Remesher");
    resurfacerMesher.getResurfacerElementTypeOption().setSelected(ResurfacerElementTypeOption.Type.QUAD);

    Units mmUnits = (Units) simulation_0.getUnitsManager().getObject("mm");
    autoMeshOperation.getDefaultValues().get(BaseSize.class).setValueAndUnits(AS_length, mmUnits);

    PartsTargetSurfaceSize targetSize = autoMeshOperation.getDefaultValues().get(PartsTargetSurfaceSize.class);
    PartsMinimumSurfaceSize minSize = autoMeshOperation.getDefaultValues().get(PartsMinimumSurfaceSize.class);

    targetSize.getRelativeOrAbsoluteOption().setSelected(RelativeOrAbsoluteOption.Type.ABSOLUTE);
    minSize.getRelativeOrAbsoluteOption().setSelected(RelativeOrAbsoluteOption.Type.ABSOLUTE);
    targetSize.getAbsoluteSizeValue().setValueAndUnits(AS_length, mmUnits);
    minSize.getAbsoluteSizeValue().setValueAndUnits(AS_length, mmUnits);

    simulation_0.get(MeshPipelineController.class).generateSurfaceMesh();

    // Export Centroids
    exportCentroids(simulation_0, guideCurvePart);
  }

  private void translateSurface(MeshPart meshPart, String surfaceName, 
      SurfaceMeshWidgetSelectController selectController, 
      SurfaceMeshWidgetRepairController repairController, 
      LabCoordinateSystem coordSystem, double length, double[] direction) {

    PartSurface surface = meshPart.getPartSurfaceManager().getPartSurface(surfaceName);
    selectController.selectPartSurface(surface);
    repairController.translateSelectedFaces(3, new DoubleVector(direction), length, coordSystem, false);

    SurfaceMeshWidgetDiagnosticsController diagnosticsController =
        selectController.getWidget().getControllers().getController(SurfaceMeshWidgetDiagnosticsController.class);
    diagnosticsController.setCheckSoftFeatureErrors(false);
    diagnosticsController.setSoftFeatureErrorsActive(false);
    diagnosticsController.setCheckHardFeatureErrors(false);
    diagnosticsController.setHardFeatureErrorsActive(false);
  }

private void exportCentroids(Simulation simulation, MeshPart guideCurvePart) {
    String[] surfaceNames = { "Left_Surface", "Bottom_Surface_I", "Right_Surface", "Bottom_Surface_II" };
    String[] fileNames = {
        "Left_Side_Co-ordinates.csv",
        "Bottom_I_Side_Co-ordinates.csv",
        "Right_Side_Co-ordinates.csv",
        "Bottom_II_Side_Co-ordinates.csv"
    };

    // Get the simulation directory
    String simDir = simulation.getSessionDir();
    String outputFolder = simDir + "/co-ordinate_in_CSV";

    // Create the folder if it doesn't exist
    java.io.File folder = new java.io.File(outputFolder);
    if (!folder.exists()) {
        folder.mkdirs();
    }

    XyzInternalTable xyzTable = simulation.getTableManager().createTable(XyzInternalTable.class);
    PrimitiveFieldFunction centroidFunction = 
        (PrimitiveFieldFunction) simulation.getFieldFunctionManager().getFunction("Centroid");

    xyzTable.setFieldFunctions(new NeoObjectVector(new Object[] {
        centroidFunction.getMagnitudeFunction(),
        centroidFunction.getComponentFunction(0),
        centroidFunction.getComponentFunction(1),
        centroidFunction.getComponentFunction(2)
    }));

    xyzTable.getParts().setQuery(null);

    for (int i = 0; i < surfaceNames.length; i++) {
        PartSurface surface = guideCurvePart.getPartSurfaceManager().getPartSurface(surfaceNames[i]);
        xyzTable.getParts().setObjects(surface);
        xyzTable.extract();

        String fullPath = outputFolder + "/" + fileNames[i];
        xyzTable.export(fullPath, ",");
        xyzTable.getParts().setQuery(null);
    }

    simulation.println("CSV coordinate files saved to: " + outputFolder);
}
}
