import { useEffect, useRef, useState, type ReactNode } from "react";

type Props = {
  label: string;
  children: ReactNode;
  className?: string;
};

export function Field({ label, children, className = "" }: Props) {
  return (
    <label className={`field ${className}`.trim()}>
      <span className="field-label">{label}</span>
      {children}
    </label>
  );
}

type SelectProps = {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
  disabled?: boolean;
  placeholder?: string;
};

export function SelectField({ label, value, onChange, options, disabled, placeholder }: SelectProps) {
  return (
    <Field label={label}>
      <select value={value} onChange={(e) => onChange(e.target.value)} disabled={disabled}>
        <option value="">{placeholder ?? "—"}</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </Field>
  );
}

type CompactSelectProps = Omit<SelectProps, "label"> & {
  label?: string;
};

export function CompactSelect({ label, value, onChange, options, disabled, placeholder }: CompactSelectProps) {
  return (
    <div className="filter-control filter-cell">
      {label && <span className="filter-control-label">{label}</span>}
      <select
        className="filter-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        <option value="">{placeholder ?? "—"}</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}

type FilterDropdownOption = { value: string; label: string; slug?: string };

type FilterDropdownGroup = {
  header?: string;
  options: FilterDropdownOption[];
};

function flattenDropdownOptions(
  options: FilterDropdownOption[] | undefined,
  groups: FilterDropdownGroup[] | undefined,
): FilterDropdownOption[] {
  if (options?.length) return options;
  if (!groups?.length) return [];
  return groups.flatMap((group) => group.options);
}

type FilterDropdownProps = {
  placeholder: string;
  anyLabel: string;
  value: string;
  onChange: (v: string) => void;
  options?: FilterDropdownOption[];
  groups?: FilterDropdownGroup[];
  disabled?: boolean;
  resetLabel?: string;
  panelClassName?: string;
};

function FilterDropdownCell({
  placeholder,
  anyLabel,
  value,
  onChange,
  options,
  groups,
  disabled,
  resetLabel,
  panelClassName,
  className = "",
}: FilterDropdownProps & { className?: string }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const flatOptions = flattenDropdownOptions(options, groups);
  const selected = flatOptions.find((o) => o.value === value);
  const triggerLabel = selected?.label ?? placeholder;

  useEffect(() => {
    if (!open) return;
    const onDocClick = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  const selectOption = (optionValue: string) => {
    onChange(optionValue);
    setOpen(false);
  };

  const renderOptions = (items: FilterDropdownOption[]) =>
    items.map((opt) => (
      <button
        key={opt.value}
        type="button"
        role="option"
        aria-selected={value === opt.value}
        className={`filter-dropdown-option ${value === opt.value ? "active" : ""}`}
        onClick={() => selectOption(opt.value)}
      >
        {opt.label}
      </button>
    ));

  return (
    <div
      className={`filter-dropdown ${className} ${open ? "open" : ""} ${value ? "has-value" : ""}`.trim()}
      ref={rootRef}
    >
      <button
        type="button"
        className="filter-dropdown-trigger filter-select"
        onClick={() => !disabled && setOpen((prev) => !prev)}
        aria-expanded={open}
        aria-haspopup="listbox"
        disabled={disabled}
      >
        <span>{triggerLabel}</span>
      </button>
      {open && (
        <div
          className={`filter-dropdown-panel ${panelClassName ?? ""}`.trim()}
          role="listbox"
          aria-label={placeholder}
        >
          <button
            type="button"
            className={`filter-dropdown-clear ${!value ? "active" : ""}`}
            onClick={() => selectOption("")}
          >
            {resetLabel ?? `× ${anyLabel}`}
          </button>
          <div className="filter-dropdown-list">
            {options?.length ? renderOptions(options) : null}
            {groups?.map((group, index) => (
              <div key={group.header ?? `group-${index}`} className="filter-dropdown-group">
                {group.header && <div className="filter-dropdown-group-header">{group.header}</div>}
                {renderOptions(group.options)}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function FilterDropdown(props: FilterDropdownProps) {
  return <FilterDropdownCell {...props} className="filter-cell" />;
}

type FilterDropdownRangeProps = {
  fromValue: string;
  toValue: string;
  onFromChange: (v: string) => void;
  onToChange: (v: string) => void;
  fromPlaceholder: string;
  toPlaceholder: string;
  anyLabel: string;
  options: FilterDropdownOption[];
  resetLabel?: string;
  panelClassName?: string;
};

export function FilterDropdownRange({
  fromValue,
  toValue,
  onFromChange,
  onToChange,
  fromPlaceholder,
  toPlaceholder,
  anyLabel,
  options,
  resetLabel,
  panelClassName,
}: FilterDropdownRangeProps) {
  const shared = { anyLabel, options, resetLabel, panelClassName };
  return (
    <div className="filter-range filter-cell">
      <div className="filter-range-inputs filter-range-inputs-dropdown">
        <FilterDropdownCell
          {...shared}
          placeholder={fromPlaceholder}
          value={fromValue}
          onChange={onFromChange}
          className="filter-dropdown-in-range"
        />
        <FilterDropdownCell
          {...shared}
          placeholder={toPlaceholder}
          value={toValue}
          onChange={onToChange}
          className="filter-dropdown-in-range"
        />
      </div>
    </div>
  );
}

type FilterPresetRangeProps = {
  fromValue: string;
  toValue: string;
  onFromChange: (v: string) => void;
  onToChange: (v: string) => void;
  fromPlaceholder: string;
  toPlaceholder: string;
  presets: number[];
  formatPreset: (value: number) => string;
  anyPresetLabel: string;
  inputMode?: "numeric" | "decimal";
};

function PresetCombo({
  value,
  onChange,
  placeholder,
  presets,
  formatPreset,
  anyPresetLabel,
  inputMode = "numeric",
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  presets: number[];
  formatPreset: (value: number) => string;
  anyPresetLabel: string;
  inputMode?: "numeric" | "decimal";
}) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDocClick = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  const selectPreset = (preset: number | null) => {
    onChange(preset === null ? "" : String(preset));
    setOpen(false);
  };

  return (
    <div className={`filter-preset-combo ${open ? "open" : ""}`} ref={rootRef}>
      <input
        className="filter-input"
        type="text"
        inputMode={inputMode}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
      <button
        type="button"
        className="filter-preset-toggle"
        aria-label={placeholder}
        aria-expanded={open}
        onClick={() => setOpen((prev) => !prev)}
      />
      {open && (
        <div className="filter-preset-panel" role="listbox">
          <button type="button" className="filter-preset-option" onClick={() => selectPreset(null)}>
            {anyPresetLabel}
          </button>
          {presets.map((preset) => (
            <button
              key={preset}
              type="button"
              className={`filter-preset-option ${value === String(preset) ? "active" : ""}`}
              onClick={() => selectPreset(preset)}
            >
              {formatPreset(preset)}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export function FilterPresetRange({
  fromValue,
  toValue,
  onFromChange,
  onToChange,
  fromPlaceholder,
  toPlaceholder,
  presets,
  formatPreset,
  anyPresetLabel,
  inputMode = "numeric",
}: FilterPresetRangeProps) {
  return (
    <div className="filter-range filter-cell">
      <div className="filter-range-inputs filter-range-inputs-preset">
        <PresetCombo
          value={fromValue}
          onChange={onFromChange}
          placeholder={fromPlaceholder}
          presets={presets}
          formatPreset={formatPreset}
          anyPresetLabel={anyPresetLabel}
          inputMode={inputMode}
        />
        <PresetCombo
          value={toValue}
          onChange={onToChange}
          placeholder={toPlaceholder}
          presets={presets}
          formatPreset={formatPreset}
          anyPresetLabel={anyPresetLabel}
          inputMode={inputMode}
        />
      </div>
    </div>
  );
}

type RangeProps = {
  label: string;
  fromValue: string;
  toValue: string;
  onFromChange: (v: string) => void;
  onToChange: (v: string) => void;
  fromPlaceholder?: string;
  toPlaceholder?: string;
  type?: string;
  hideLabel?: boolean;
};

export function RangeControl({
  label,
  fromValue,
  toValue,
  onFromChange,
  onToChange,
  fromPlaceholder,
  toPlaceholder,
  type = "text",
  hideLabel = false,
}: RangeProps) {
  return (
    <div className="filter-range filter-cell">
      {!hideLabel && <span className="filter-range-label">{label}</span>}
      <div className="filter-range-inputs">
        <input
          className="filter-input"
          type={type}
          value={fromValue}
          onChange={(e) => onFromChange(e.target.value)}
          placeholder={fromPlaceholder}
        />
        <input
          className="filter-input"
          type={type}
          value={toValue}
          onChange={(e) => onToChange(e.target.value)}
          placeholder={toPlaceholder}
        />
      </div>
    </div>
  );
}

type InputProps = {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
};

export function InputField({ label, value, onChange, type = "text", placeholder }: InputProps) {
  return (
    <Field label={label}>
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} />
    </Field>
  );
}

type CheckProps = {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
};

export function CheckboxField({ label, checked, onChange }: CheckProps) {
  return (
    <label className="checkbox-field">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

type SegmentOption = { value: string; label: string };

type SegmentProps = {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: SegmentOption[];
};

export function RadioSegment({ label, value, onChange, options }: SegmentProps) {
  return (
    <div className="filter-segment filter-cell">
      <span className="filter-segment-label">{label}</span>
      <div className="filter-segment-options" role="radiogroup" aria-label={label}>
        {options.map((opt) => (
          <label key={opt.value || "__any"} className={`filter-segment-option ${value === opt.value ? "active" : ""}`}>
            <input
              type="radio"
              name={label}
              value={opt.value}
              checked={value === opt.value}
              onChange={() => onChange(opt.value)}
            />
            <span>{opt.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

const COLOR_SWATCH: Record<string, string> = {
  white: "#f5f5f5",
  black: "#1a1d21",
  brown: "#6b4423",
  purple: "#7b5ea7",
  green: "#3d8b4a",
  silver: "#b8bec6",
  gray: "#b8bec6",
  blue: "#4a7fd4",
  yellow: "#e8c547",
  beige: "#d4b896",
  red: "#c0392b",
  orange: "#e67e22",
  pink: "#e88aab",
  burgundy: "#7b1e3a",
};

type ColorPickerProps = {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string; slug?: string }[];
  anyLabel: string;
};

export function ColorPickerField({ label, value, onChange, options, anyLabel }: ColorPickerProps) {
  return (
    <div className="filter-color filter-cell">
      <span className="filter-color-label">{label}</span>
      <div className="filter-color-options">
        <button
          type="button"
          className={`filter-color-any ${!value ? "active" : ""}`}
          onClick={() => onChange("")}
        >
          {anyLabel}
        </button>
        {options.map((opt) => {
          const slug = opt.slug || opt.label.toLowerCase();
          const bg = COLOR_SWATCH[slug] || "#ccc";
          return (
            <button
              key={opt.value}
              type="button"
              className={`filter-color-swatch ${value === opt.value ? "active" : ""}`}
              style={{ background: bg }}
              title={opt.label}
              aria-label={opt.label}
              onClick={() => onChange(value === opt.value ? "" : opt.value)}
            />
          );
        })}
      </div>
    </div>
  );
}

function BodyTypeIcon({ slug }: { slug: string }) {
  const common = { viewBox: "0 0 64 32", fill: "none", stroke: "currentColor", strokeWidth: "2" };
  switch (slug) {
    case "sedan":
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M10 20l6-8h20l8 8M14 24a3 3 0 1 0 6 0M44 24a3 3 0 1 0 6 0" />
        </svg>
      );
    case "hatchback-5d":
    case "hatchback-3d":
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M10 20l8-9h14l10 9M14 24a3 3 0 1 0 6 0M44 24a3 3 0 1 0 6 0" />
          <path d="M32 11v9" />
        </svg>
      );
    case "liftback":
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M10 20l8-9h16l6 9M14 24a3 3 0 1 0 6 0M44 24a3 3 0 1 0 6 0" />
          <path d="M34 11l6 9" />
        </svg>
      );
    case "suv-5d":
    case "suv-3d":
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M8 20l8-10h24l8 10M14 24a3 3 0 1 0 6 0M44 24a3 3 0 1 0 6 0" />
        </svg>
      );
    case "wagon":
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M10 20l6-8h26l6 8M14 24a3 3 0 1 0 6 0M44 24a3 3 0 1 0 6 0" />
          <path d="M42 12v8" />
        </svg>
      );
    case "minivan":
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M8 20l6-11h28l6 11M14 24a3 3 0 1 0 6 0M44 24a3 3 0 1 0 6 0" />
        </svg>
      );
    case "pickup":
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M10 20l6-8h14l4 8h16M14 24a3 3 0 1 0 6 0M48 24a3 3 0 1 0 6 0" />
        </svg>
      );
    case "coupe":
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M12 20l10-11h16l8 11M14 24a3 3 0 1 0 6 0M44 24a3 3 0 1 0 6 0" />
        </svg>
      );
    case "convertible":
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M12 20l8-6h20l8 6M14 24a3 3 0 1 0 6 0M44 24a3 3 0 1 0 6 0" />
          <path d="M20 14h24" strokeDasharray="3 3" />
        </svg>
      );
    default:
      return (
        <svg {...common} aria-hidden>
          <path d="M6 20h52M10 20l6-8h28l6 8M14 24a3 3 0 1 0 6 0M44 24a3 3 0 1 0 6 0" />
        </svg>
      );
  }
}

type BodyTypePickerProps = {
  placeholder: string;
  anyLabel: string;
  countLabel: (count: number) => string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string; slug?: string }[];
};

function parseSelectedBodyTypes(value: string): string[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

export function BodyTypePickerField({
  placeholder,
  anyLabel,
  countLabel,
  value,
  onChange,
  options,
}: BodyTypePickerProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const selectedIds = parseSelectedBodyTypes(value);
  const selectedOptions = options.filter((o) => selectedIds.includes(o.value));

  const triggerLabel = (() => {
    if (selectedOptions.length === 0) return placeholder;
    if (selectedOptions.length === 1) return selectedOptions[0].label;
    return countLabel(selectedOptions.length);
  })();

  const toggleOption = (optionValue: string) => {
    const next = selectedIds.includes(optionValue)
      ? selectedIds.filter((id) => id !== optionValue)
      : [...selectedIds, optionValue];
    onChange(next.join(","));
  };

  useEffect(() => {
    if (!open) return;
    const onDocClick = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  return (
    <div className={`filter-body-type filter-cell ${open ? "open" : ""}`} ref={rootRef}>
      <button
        type="button"
        className="filter-body-type-trigger filter-select"
        onClick={() => setOpen((prev) => !prev)}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <span>{triggerLabel}</span>
      </button>
      {open && (
        <div className="filter-body-type-panel" role="listbox" aria-label={placeholder} aria-multiselectable="true">
          <button
            type="button"
            className={`filter-body-type-clear ${selectedIds.length === 0 ? "active" : ""}`}
            onClick={() => onChange("")}
          >
            × {anyLabel}
          </button>
          <div className="filter-body-type-grid">
            {options.map((opt) => {
              const active = selectedIds.includes(opt.value);
              return (
                <button
                  key={opt.value}
                  type="button"
                  role="option"
                  aria-selected={active}
                  className={`filter-body-type-option ${active ? "active" : ""}`}
                  onClick={() => toggleOption(opt.value)}
                >
                  <span className="filter-body-type-icon">
                    <BodyTypeIcon slug={opt.slug || opt.value} />
                  </span>
                  <span className="filter-body-type-label">{opt.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
