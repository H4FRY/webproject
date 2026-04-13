import { Routes, Route } from "react-router-dom";
import WelcomePage from "./pages/WelcomePage";
import RegisterPage from "./pages/RegisterPage";
import Page2fa from "./pages/Page2fa";
import LoginPage from "./pages/LoginPage";
import MfaPage from "./pages/MfaPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<WelcomePage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/register/confirm-2fa" element={<Page2fa />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/login/verify-2fa" element={<MfaPage />} />
    </Routes>
  );
}

export default App;