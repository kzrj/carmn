import { ChangeEvent, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { uploadListingPhoto } from "../api/listings";
import { getLocale } from "../lib/i18n";
import { t } from "../lib/labels";
import { formatApiError } from "../lib/sellForm";

export default function SellPhotosPage() {
  const locale = getLocale();
  const navigate = useNavigate();
  const { id } = useParams();
  const listingId = Number(id);

  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(0);
  const [error, setError] = useState("");

  const onFiles = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length || !listingId) return;

    setError("");
    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        await uploadListingPhoto(listingId, file);
        setUploaded((n) => n + 1);
      }
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const finish = () => navigate(`/listing/${listingId}`);

  if (!listingId) {
    return <p className="error page-pad">Invalid listing</p>;
  }

  return (
    <div className="sell-page page-pad">
      <h1>{t("photosTitle", locale)}</h1>
      <p className="muted">{t("photosHint", locale)}</p>

      <div className="card sell-card">
        <label className="btn btn-ghost sell-file-btn">
          {uploading ? t("loading", locale) : t("addPhotos", locale)}
          <input type="file" accept="image/*" multiple hidden onChange={onFiles} disabled={uploading} />
        </label>

        {uploaded > 0 && <p className="muted">{uploaded} uploaded</p>}
        {error && <p className="error">{error}</p>}

        <div className="sell-actions">
          <button type="button" className="btn btn-primary" onClick={finish}>
            {t("publish", locale)}
          </button>
          <button type="button" className="btn btn-ghost" onClick={finish}>
            {t("skipPhotos", locale)}
          </button>
        </div>
      </div>
    </div>
  );
}
