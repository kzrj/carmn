import { getPaginationItems } from "../../lib/pagination";
import { getLocale } from "../../lib/i18n";
import { t } from "../../lib/labels";

type PaginationProps = {
  page: number;
  totalPages: number;
  loading?: boolean;
  onPageChange: (page: number) => void;
};

export default function Pagination({ page, totalPages, loading, onPageChange }: PaginationProps) {
  const locale = getLocale();

  if (totalPages <= 1) return null;

  const items = getPaginationItems(page, totalPages);

  return (
    <nav className="pagination" aria-label="Pagination">
      <button
        type="button"
        className="pagination-nav"
        disabled={loading || page <= 1}
        aria-label={t("paginationPrev", locale)}
        onClick={() => onPageChange(page - 1)}
      >
        {t("paginationPrev", locale)}
      </button>

      {items.map((item, index) =>
        item === "ellipsis" ? (
          <span key={`ellipsis-${index}`} className="pagination-ellipsis" aria-hidden="true">
            …
          </span>
        ) : (
          <button
            key={item}
            type="button"
            className={item === page ? "active" : ""}
            disabled={loading}
            aria-current={item === page ? "page" : undefined}
            onClick={() => onPageChange(item)}
          >
            {item}
          </button>
        ),
      )}

      <button
        type="button"
        className="pagination-nav"
        disabled={loading || page >= totalPages}
        aria-label={t("paginationNext", locale)}
        onClick={() => onPageChange(page + 1)}
      >
        {t("paginationNext", locale)}
      </button>
    </nav>
  );
}
