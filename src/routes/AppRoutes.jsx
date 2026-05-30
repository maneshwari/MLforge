import { Routes, Route } from "react-router-dom";

import Home from "../pages/Home";
import Dashboard from "../pages/Dashboard";
import ChooseTemplate from "../pages/ChooseTemplate";
import CreateProject from "../pages/CreateProject";
import DatasetIntelligence from "../pages/DatasetIntelligence";
import Recommendations from "../pages/Recommendations";
import ProjectBlueprint from "../pages/ProjectBlueprint";
import Training from "../pages/Training";
import Results from "../pages/Results";


function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/templates" element={<ChooseTemplate />} />
      <Route path="/create-project" element={<CreateProject />} />
      <Route
        path="/dataset-intelligence"
        element={<DatasetIntelligence />}
      />
      <Route
  path="/recommendations"
  element={<Recommendations />}
/>
      <Route
        path="/blueprint"
        element={<ProjectBlueprint />}
      />
      <Route
        path="/training"
        element={<Training />}
      />
      <Route
        path="/results"
        element={<Results />}
      />
    </Routes>
  );
}

export default AppRoutes;