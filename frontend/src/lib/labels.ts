import type { Locale } from "../types";

type LabelKey =
  | "catalog"
  | "filters"
  | "extended"
  | "show"
  | "showListings"
  | "reset"
  | "loading"
  | "noResults"
  | "found"
  | "back"
  | "login"
  | "register"
  | "logout"
  | "price"
  | "year"
  | "mileage"
  | "description"
  | "specs"
  | "seller"
  | "all"
  | "used"
  | "new"
  | "unsold"
  | "withPhotos"
  | "allRegions"
  | "otherCity"
  | "brand"
  | "model"
  | "generation"
  | "transmission"
  | "fuel"
  | "drive"
  | "engineVolume"
  | "from"
  | "to"
  | "sort"
  | "priceFrom"
  | "yearFrom"
  | "engineFrom"
  | "showAll"
  | "postAd"
  | "postAdTitle"
  | "postAdVinHint"
  | "vin"
  | "vinPlaceholder"
  | "continue"
  | "vinStubTitle"
  | "vinStubText"
  | "fillManual"
  | "manualTitle"
  | "trim"
  | "condition"
  | "region"
  | "city"
  | "priceMnt"
  | "priceUsd"
  | "chassis"
  | "submit"
  | "photosTitle"
  | "photosHint"
  | "addPhotos"
  | "skipPhotos"
  | "publish"
  | "loginRequired"
  | "selectBrand"
  | "selectModel"
  | "selectYear"
  | "selectCity"
  | "bodyType"
  | "paginationPrev"
  | "paginationNext"
  | "shownOf"
  | "ofTotal"
  | "viewListings"
  | "viewModelLineup"
  | "noModelGroups"
  | "groupsSortCount"
  | "groupsSortName"
  | "tabListings"
  | "tabModels"
  | "listingsCountShort"
  | "normalSearch"
  | "resetAll"
  | "documents"
  | "damageLabel"
  | "steeringLabel"
  | "powerPts"
  | "powerFrom"
  | "mileageFrom"
  | "noLocalMileage"
  | "brandCountry"
  | "availabilityLabel"
  | "ownersCount"
  | "exchange"
  | "certification"
  | "keywords"
  | "keywordsPlaceholder"
  | "any"
  | "ptsOk"
  | "ptsProblem"
  | "damageOk"
  | "damageRepair"
  | "availInStock"
  | "availInTransit"
  | "availOnOrder"
  | "colorAny"
  | "bodyTypeLabel"
  | "bodyAny"
  | "bodyTypesCount"
  | "colorLabel"
  | "steeringAny"
  | "steeringLeft"
  | "steeringRight"
  | "sellerAny"
  | "sellerOwner"
  | "sellerPrivate"
  | "sellerCompany"
  | "ownersAny"
  | "ownersOne"
  | "ownersTwo"
  | "ownersThree"
  | "radius100"
  | "radius200"
  | "radius500"
  | "radius1000"
  | "transmissionAutomaticGroup"
  | "anyYear"
  | "anyVolume"
  | "anyPrice";

const LABELS: Record<LabelKey, Record<Locale, string>> = {
  catalog: { mn: "Зар", ru: "Объявления", en: "Listings" },
  filters: { mn: "Шүүлтүүр", ru: "Фильтры", en: "Filters" },
  extended: { mn: "Өргөтгөсөн хайлт", ru: "Расширенный поиск", en: "Advanced search" },
  show: { mn: "Харуулах", ru: "Показать", en: "Show" },
  showListings: { mn: "Зар харуулах", ru: "Показать объявления", en: "Show listings" },
  reset: { mn: "Цэвэрлэх", ru: "Сбросить", en: "Reset" },
  loading: { mn: "Ачааллаж байна...", ru: "Загрузка...", en: "Loading..." },
  noResults: { mn: "Зар олдсонгүй", ru: "Объявлений нет", en: "No listings found" },
  found: { mn: "олдлоо", ru: "найдено", en: "found" },
  back: { mn: "Буцах", ru: "Назад", en: "Back" },
  login: { mn: "Нэвтрэх", ru: "Вход", en: "Login" },
  register: { mn: "Бүртгүүлэх", ru: "Регистрация", en: "Register" },
  logout: { mn: "Гарах", ru: "Выход", en: "Logout" },
  price: { mn: "Үнэ", ru: "Цена", en: "Price" },
  year: { mn: "Он", ru: "Год", en: "Year" },
  mileage: { mn: "Явсан", ru: "Пробег", en: "Mileage" },
  description: { mn: "Тайлбар", ru: "Описание", en: "Description" },
  specs: { mn: "Мэдээлэл", ru: "Характеристики", en: "Specifications" },
  seller: { mn: "Зарлагч", ru: "Продавец", en: "Seller" },
  all: { mn: "Бүгд", ru: "Все", en: "All" },
  used: { mn: "Хэрэглэсэн", ru: "С пробегом", en: "Used" },
  new: { mn: "Шинэ", ru: "Новые", en: "New" },
  unsold: { mn: "Зараагдаагүй", ru: "Непроданные", en: "Unsold" },
  withPhotos: { mn: "Зурагтай", ru: "С фото", en: "With photos" },
  allRegions: { mn: "Бүх бүс", ru: "Все регионы", en: "All regions" },
  otherCity: { mn: "Өөр хот", ru: "Другой город", en: "Other city" },
  brand: { mn: "Марк", ru: "Марка", en: "Brand" },
  model: { mn: "Загвар", ru: "Модель", en: "Model" },
  generation: { mn: "Үе", ru: "Поколение", en: "Generation" },
  transmission: { mn: "КПП", ru: "КПП", en: "Transmission" },
  fuel: { mn: "Түлш", ru: "Топливо", en: "Fuel" },
  drive: { mn: "Хөтлөгч", ru: "Привод", en: "Drive" },
  engineVolume: { mn: "Объем, л", ru: "Объем, л", en: "Engine, L" },
  from: { mn: "от", ru: "от", en: "from" },
  to: { mn: "до", ru: "до", en: "to" },
  sort: { mn: "Эрэмбэ", ru: "Сортировка", en: "Sort" },
  priceFrom: { mn: "Үнэ от, ₮", ru: "Цена от, ₮", en: "Price from, ₮" },
  yearFrom: { mn: "Он от", ru: "Год от", en: "Year from" },
  engineFrom: { mn: "Объем от, л", ru: "Объем от, л", en: "Engine from, L" },
  showAll: { mn: "Бүгдийг харуулах", ru: "Показать все", en: "Show all" },
  postAd: { mn: "+ Зар нэмэх", ru: "+ Подать объявление", en: "+ Post ad" },
  postAdTitle: {
    mn: "Автомашины зар нэмэх",
    ru: "Подать объявление о продаже автомобиля",
    en: "Post a car for sale",
  },
  postAdVinHint: {
    mn: "VIN оруулбал талбаруудыг автоматаар бөглөнө (удахгүй)",
    ru: "Введите VIN — ключевые поля заполнятся автоматически (скоро)",
    en: "Enter VIN to auto-fill key fields (coming soon)",
  },
  vin: { mn: "VIN", ru: "VIN", en: "VIN" },
  vinPlaceholder: {
    mn: "VIN / аралын дугаар",
    ru: "Введите VIN/номер кузова",
    en: "Enter VIN/chassis number",
  },
  continue: { mn: "Үргэлжлүүлэх", ru: "Продолжить", en: "Continue" },
  vinStubTitle: {
    mn: "VIN-ээр автоматаар бөглөх удахгүй",
    ru: "Автозаполнение по VIN скоро",
    en: "VIN auto-fill coming soon",
  },
  vinStubText: {
    mn: "Одоогоор VIN-ээр шалгах боломжгүй. Гараар бөглөнө үү.",
    ru: "Проверка VIN пока недоступна. Заполните объявление самостоятельно.",
    en: "VIN lookup is not available yet. Please fill in the form manually.",
  },
  fillManual: {
    mn: "Гараар бөглөх",
    ru: "Заполнить самостоятельно",
    en: "Fill in manually",
  },
  manualTitle: {
    mn: "Зарын мэдээлэл",
    ru: "Данные объявления",
    en: "Listing details",
  },
  trim: { mn: "Комплектаци", ru: "Комплектация", en: "Trim" },
  condition: { mn: "Төлөв", ru: "Состояние", en: "Condition" },
  region: { mn: "Бүс", ru: "Регион", en: "Region" },
  city: { mn: "Хот", ru: "Город", en: "City" },
  priceMnt: { mn: "Үнэ, ₮", ru: "Цена, ₮", en: "Price, MNT" },
  priceUsd: { mn: "Үнэ, $", ru: "Цена, $", en: "Price, USD" },
  chassis: { mn: "Аралын дугаар", ru: "Номер кузова", en: "Chassis number" },
  submit: { mn: "Нийтлэх", ru: "Опубликовать", en: "Publish" },
  photosTitle: { mn: "Зураг нэмэх", ru: "Добавить фото", en: "Add photos" },
  photosHint: {
    mn: "Зураг нэмж болно эсвэл алгасаж болно",
    ru: "Можно добавить фото или пропустить",
    en: "Add photos or skip for now",
  },
  addPhotos: { mn: "Зураг сонгох", ru: "Выбрать фото", en: "Choose photos" },
  skipPhotos: { mn: "Алгасах", ru: "Пропустить", en: "Skip" },
  publish: { mn: "Дуусгах", ru: "Готово", en: "Done" },
  loginRequired: {
    mn: "Нийтлэхийн тулд нэвтэрнэ үү",
    ru: "Войдите, чтобы опубликовать",
    en: "Log in to publish",
  },
  selectBrand: { mn: "Марк сонгох", ru: "Выберите марку", en: "Select brand" },
  selectModel: { mn: "Загвар сонгох", ru: "Выберите модель", en: "Select model" },
  selectYear: { mn: "Он сонгох", ru: "Выберите год", en: "Select year" },
  selectCity: { mn: "Хот сонгох", ru: "Выберите город", en: "Select city" },
  bodyType: { mn: "Төрөл", ru: "Кузов", en: "Body type" },
  paginationPrev: { mn: "← Өмнөх", ru: "← Назад", en: "← Prev" },
  paginationNext: { mn: "Дараах →", ru: "Далее →", en: "Next →" },
  shownOf: { mn: "Харуулж байна", ru: "Показано", en: "Showing" },
  ofTotal: { mn: "-с", ru: "из", en: "of" },
  viewListings: { mn: "Зар", ru: "Объявления", en: "Listings" },
  viewModelLineup: { mn: "Загварын жагсаалт", ru: "Модельный ряд", en: "By model" },
  noModelGroups: { mn: "Загвар олдсонгүй", ru: "Модели не найдены", en: "No models found" },
  groupsSortCount: { mn: "Тоогоор", ru: "По количеству", en: "By count" },
  groupsSortName: { mn: "Нэрээр", ru: "По названию", en: "By name" },
  tabListings: { mn: "зар", ru: "объявления", en: "listings" },
  tabModels: { mn: "загвар", ru: "моделей", en: "models" },
  listingsCountShort: { mn: "зар", ru: "объявлений", en: "listings" },
  normalSearch: { mn: "Энгийн хайлт", ru: "Обычный поиск", en: "Basic search" },
  resetAll: { mn: "Бүгдийг цэвэрлэх", ru: "Сбросить все", en: "Reset all" },
  documents: { mn: "Баримт", ru: "Документы", en: "Documents" },
  damageLabel: { mn: "Гэмтэл", ru: "Повреждения", en: "Damage" },
  steeringLabel: { mn: "Хүрмэн", ru: "Руль", en: "Steering" },
  powerPts: { mn: "Хүч, л.с.", ru: "Мощность по ПТС", en: "Power, hp" },
  powerFrom: { mn: "от, л.с.", ru: "от, л.с.", en: "from, hp" },
  mileageFrom: { mn: "от, км", ru: "от, км", en: "from, km" },
  noLocalMileage: { mn: "Монголд явсангүй", ru: "Без пробега по РФ", en: "No local mileage" },
  brandCountry: { mn: "Маркийн улс", ru: "Страна марки", en: "Brand country" },
  availabilityLabel: { mn: "Байдал", ru: "Наличие", en: "Availability" },
  ownersCount: { mn: "Эзэмшигч", ru: "Количество владельцев", en: "Owners" },
  exchange: { mn: "Солилт", ru: "Возможен обмен", en: "Exchange possible" },
  certification: { mn: "Баталгаажсан", ru: "Сертификация", en: "Certified" },
  keywords: { mn: "Түлхүүр үг", ru: "Ключевые слова", en: "Keywords" },
  keywordsPlaceholder: {
    mn: "Жишээ нь \"нэг эзэн\"",
    ru: 'Для точного соответствия используйте кавычки. Например, "один хозяин".',
    en: 'Use quotes for exact match, e.g. "one owner".',
  },
  any: { mn: "Байхгүй", ru: "Неважно", en: "Any" },
  ptsOk: { mn: "Зөв", ru: "В порядке", en: "In order" },
  ptsProblem: { mn: "Асуудалтай", ru: "Нет или проблемные", en: "Missing or problematic" },
  damageOk: { mn: "Засваргүй", ru: "Не требуется ремонт", en: "No repair needed" },
  damageRepair: { mn: "Засвар шаардлагатай", ru: "Требуется ремонт или не на ходу", en: "Needs repair" },
  availInStock: { mn: "Байгаа", ru: "В наличии", en: "In stock" },
  availInTransit: { mn: "Замд", ru: "В пути", en: "In transit" },
  availOnOrder: { mn: "Захиалгаар", ru: "Под заказ", en: "On order" },
  colorAny: { mn: "Бүгд", ru: "Любой", en: "Any" },
  bodyTypeLabel: { mn: "Бие", ru: "Тип кузова", en: "Body type" },
  bodyAny: { mn: "Бүх бие", ru: "Любой кузов", en: "Any body" },
  bodyTypesCount: { mn: "{n} бие", ru: "{n} типа кузова", en: "{n} body types" },
  colorLabel: { mn: "Өнгө", ru: "Цвет", en: "Color" },
  steeringAny: { mn: "Бүгд", ru: "Любой", en: "Any" },
  steeringLeft: { mn: "Зүүн", ru: "Левый", en: "Left" },
  steeringRight: { mn: "Баруун", ru: "Правый", en: "Right" },
  sellerAny: { mn: "Бүгд", ru: "Любой", en: "Any" },
  sellerOwner: { mn: "Эзэн", ru: "Собственник", en: "Owner" },
  sellerPrivate: { mn: "Хувь хүн", ru: "Частник", en: "Private" },
  sellerCompany: { mn: "Компани", ru: "Компания", en: "Company" },
  ownersAny: { mn: "Бүгд", ru: "Любое", en: "Any" },
  ownersOne: { mn: "1", ru: "Один", en: "One" },
  ownersTwo: { mn: "≤2", ru: "До двух", en: "Up to two" },
  ownersThree: { mn: "≤3", ru: "До трех", en: "Up to three" },
  radius100: { mn: "+100 км", ru: "+100 км", en: "+100 km" },
  radius200: { mn: "+200 км", ru: "+200 км", en: "+200 km" },
  radius500: { mn: "+500 км", ru: "+500 км", en: "+500 km" },
  radius1000: { mn: "+1000 км", ru: "+1000 км", en: "+1000 km" },
  transmissionAutomaticGroup: { mn: "Автомат", ru: "Автомат", en: "Automatic" },
  anyYear: { mn: "Бүх он", ru: "Любой год", en: "Any year" },
  anyVolume: { mn: "Бүх объем", ru: "Любой объем", en: "Any volume" },
  anyPrice: { mn: "Бүх үнэ", ru: "Любая цена", en: "Any price" },
};

export function t(key: LabelKey, locale: Locale): string {
  return LABELS[key][locale] || LABELS[key].mn;
}
