// Simcenter STAR-CCM+ macro: Edge_Inflation.java
// Optimized by ChatGPT

package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;
import star.meshing.*;

public class Foiling_Macro_Part_1_1 extends StarMacro {

  public void execute() {
    execute0();
  }

  private void execute0() {

    Simulation simulation_0 = getActiveSimulation();
    float Inflation_Length = 0.005f;

    PartSurfaceMeshWidget partSurfaceMeshWidget_2 = 
      simulation_0.get(PartSurfaceMeshWidget.class);

    SurfaceMeshWidgetSelectController surfaceMeshWidgetSelectController_1 = 
      partSurfaceMeshWidget_2.getControllers().getController(SurfaceMeshWidgetSelectController.class);

    SurfaceMeshWidgetRepairController surfaceMeshWidgetRepairController_0 = 
      partSurfaceMeshWidget_2.getControllers().getController(SurfaceMeshWidgetRepairController.class);

    SurfaceMeshWidgetDiagnosticsController surfaceMeshWidgetDiagnosticsController_0 = 
      partSurfaceMeshWidget_2.getControllers().getController(SurfaceMeshWidgetDiagnosticsController.class);

    LabCoordinateSystem labCoordinateSystem_0 = 
      simulation_0.getCoordinateSystemManager().getLabCoordinateSystem();

    MeshPart meshPart_1 = 
      ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("Glass"));

    String[] curveNames = { "Bottom_Curve_I", "Bottom_Curve_II" };

    for (String curveName : curveNames) {
      PartCurve partCurve = 
        ((PartCurve) meshPart_1.getPartCurveManager().getPartCurve(curveName));

      surfaceMeshWidgetSelectController_1.selectPartCurves(
          new NeoObjectVector(new Object[] {partCurve}));

      surfaceMeshWidgetRepairController_0.inflateSelectedFaces(
          false, 1, new DoubleVector(new double[] {}), Inflation_Length, 
          labCoordinateSystem_0, true);

      surfaceMeshWidgetDiagnosticsController_0.setCheckSoftFeatureErrors(false);
      surfaceMeshWidgetDiagnosticsController_0.setSoftFeatureErrorsActive(false);
      surfaceMeshWidgetDiagnosticsController_0.setCheckHardFeatureErrors(false);
      surfaceMeshWidgetDiagnosticsController_0.setHardFeatureErrorsActive(false);
    }

    surfaceMeshWidgetSelectController_1.clearSelected();
  }
}
