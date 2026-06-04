import { useEffect } from "react";
import { useParams } from "react-router-dom";
import ListingDetailView from "../components/listings/ListingDetailView";
import { getLocale } from "../lib/i18n";
import { t } from "../lib/labels";
import { listingDetailActions, listingDetailStore } from "../store/listingDetailStore";

export default function ListingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const locale = getLocale();
  const { item, loading, error } = listingDetailStore.useStore((s) => s);

  useEffect(() => {
    const numId = Number(id);
    if (numId) listingDetailActions.load(numId);
    return () => listingDetailActions.clear();
  }, [id]);

  if (loading) return <p className="muted page-pad">{t("loading", locale)}</p>;
  if (error) return <p className="error page-pad">{error}</p>;
  if (!item) return null;

  return (
    <div className="page-pad">
      <ListingDetailView item={item} />
    </div>
  );
}
