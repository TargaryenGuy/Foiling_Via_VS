// Simcenter STAR-CCM+ macro: Test_1.java
// Written by Simcenter STAR-CCM+ 18.04.008
package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;
import star.meshing.*;

public class Foiling_Macro_Part_1 extends StarMacro {

  public void execute() {
    execute0();
  }

  private void execute0() {

    Simulation simulation_0 = getActiveSimulation();
    double inflation_Length = 0.005f;
    double tolerance = 0.008f;

    PartSurfaceMeshWidget partSurfaceMeshWidget_2 = simulation_0.get(PartSurfaceMeshWidget.class);

    SurfaceMeshWidgetMergeImprintPartsController surfaceMeshWidgetMergeImprintPartsController_0 =
      partSurfaceMeshWidget_2.getControllers().getController(SurfaceMeshWidgetMergeImprintPartsController.class);

    MeshPart meshPart_0 = ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Glass"));

    PartSurface partSurface_1 = ((PartSurface) meshPart_0.getPartSurfaceManager().getPartSurface("Glass"));

    surfaceMeshWidgetMergeImprintPartsController_0.addObjectsToSecondSubset(
      new NeoObjectVector(new Object[] { partSurface_1 }));

    SurfaceMeshWidgetRepairController surfaceMeshWidgetRepairController_2 =
      partSurfaceMeshWidget_2.getControllers().getController(SurfaceMeshWidgetRepairController.class);

    SurfaceMeshWidgetMergeImprintOptions surfaceMeshWidgetMergeImprintOptions_0 =
      surfaceMeshWidgetRepairController_2.getOptions().getMergeImprintOptions();

    surfaceMeshWidgetMergeImprintOptions_0.getSourceSetMode().setSelected(
      SurfaceMeshWidgetSubsetModeType.Type.EDGES);

    MeshPart meshPart_5 = ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Seals"));

    PartCurve partCurve_1 = ((PartCurve) meshPart_5.getPartCurveManager().getPartCurve("Left_Curve"));
    //PartCurve partCurve_2 = ((PartCurve) meshPart_5.getPartCurveManager().getPartCurve("Bottom_Curve_I"));
    PartCurve partCurve_3 = ((PartCurve) meshPart_5.getPartCurveManager().getPartCurve("Right_Curve"));
    //PartCurve partCurve_5 = ((PartCurve) meshPart_5.getPartCurveManager().getPartCurve("Bottom_Curve_II"));

    surfaceMeshWidgetMergeImprintPartsController_0.addObjectsToFirstSubset(
      new NeoObjectVector(new Object[] { partCurve_1, partCurve_3 }));

    Units units_0 = ((Units) simulation_0.getUnitsManager().getObject("m"));

    surfaceMeshWidgetMergeImprintOptions_0.getToleranceQuantity().setUnits(units_0);
    surfaceMeshWidgetMergeImprintOptions_0.getToleranceQuantity().setValue(tolerance);

    surfaceMeshWidgetMergeImprintPartsController_0.mergeMultiPart();

    SurfaceMeshWidgetDiagnosticsController surfaceMeshWidgetDiagnosticsController_3 =
      partSurfaceMeshWidget_2.getControllers().getController(SurfaceMeshWidgetDiagnosticsController.class);

    surfaceMeshWidgetDiagnosticsController_3.setCheckSoftFeatureErrors(false);
    surfaceMeshWidgetDiagnosticsController_3.setSoftFeatureErrorsActive(false);
    surfaceMeshWidgetDiagnosticsController_3.setCheckHardFeatureErrors(false);
    surfaceMeshWidgetDiagnosticsController_3.setHardFeatureErrorsActive(false);

    //////////////////////////////////////////////////////////////////////////////////////////////////////////////

    SurfaceMeshWidgetSelectController surfaceMeshWidgetSelectController_2 =
      partSurfaceMeshWidget_2.getControllers().getController(SurfaceMeshWidgetSelectController.class);

    MeshPart meshPart_6 = ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Seals"));

    LabCoordinateSystem labCoordinateSystem_0 = simulation_0.getCoordinateSystemManager().getLabCoordinateSystem();

    SurfaceMeshWidgetRepairController repairController =
      partSurfaceMeshWidget_2.getControllers().getController(SurfaceMeshWidgetRepairController.class);

    SurfaceMeshWidgetDiagnosticsController diagnosticsController =
      partSurfaceMeshWidget_2.getControllers().getController(SurfaceMeshWidgetDiagnosticsController.class);

    String[] curveNames = { "Left_Curve", "Right_Curve" };

    for (String curveName : curveNames) {
      PartCurve curve = ((PartCurve) meshPart_6.getPartCurveManager().getPartCurve(curveName));
      surfaceMeshWidgetSelectController_2.selectPartCurves(new NeoObjectVector(new Object[] { curve }));

      repairController.inflateSelectedFaces(false, 1, new DoubleVector(new double[] {}), inflation_Length,
          labCoordinateSystem_0, true);

      diagnosticsController.setCheckSoftFeatureErrors(false);
      diagnosticsController.setSoftFeatureErrorsActive(false);
      diagnosticsController.setCheckHardFeatureErrors(false);
      diagnosticsController.setHardFeatureErrorsActive(false);
    }

    surfaceMeshWidgetSelectController_2.clearSelected();
  }
}
