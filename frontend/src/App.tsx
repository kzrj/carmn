import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppHeader from "./components/layout/AppHeader";
import CatalogPage from "./pages/CatalogPage";
import ListingDetailPage from "./pages/ListingDetailPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import SellManualPage from "./pages/SellManualPage";
import SellPhotosPage from "./pages/SellPhotosPage";
import SellVinPage from "./pages/SellVinPage";
import { authActions } from "./store/authStore";

export default function App() {
  useEffect(() => {
    authActions.init();
  }, []);

  return (
    <BrowserRouter>
      <div className="app-shell">
        <AppHeader />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<CatalogPage />} />
            <Route path="/sell" element={<SellVinPage />} />
            <Route path="/sell/manual" element={<SellManualPage />} />
            <Route path="/sell/photos/:id" element={<SellPhotosPage />} />
            <Route path="/listing/:id" element={<ListingDetailPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/:brandSlug/:modelSlug/:generationSlug" element={<CatalogPage />} />
            <Route path="/:brandSlug/:modelSlug" element={<CatalogPage />} />
            <Route path="/:brandSlug" element={<CatalogPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
