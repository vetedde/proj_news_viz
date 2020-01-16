# Frontend

## Настройка локального дев окружения
1. https://www.npmjs.com/get-npm
2. `npm install`

## Разработка
В директории `frontend`

* `npm run dev` - запускает дев сервер для разработки. Все изменения будут автоматически применяться в браузере.
* `npm run build` - сборка проекта для прода. Результат будет в `./dist`

## Структура

```bash
frontend
├── assets
│   └── scss
│       └── main.scss # Глобальные стили. Тут же можно поменять настроки бутстрапа
├── components
│   ├── MainViz
│   │   └── index.vue # Основная визуализация как в https://proj-news-viz-flask.herokuapp.com/
│   ├── Navbar.vue # Полоска с навигацией
│   └── README.md
├── jsconfig.json
├── layouts
│   ├── README.md
│   └── default.vue
├── middleware
│   └── README.md
├── nuxt.config.js
├── package-lock.json
├── package.json
├── pages
│   ├── README.md
│   ├── about.vue # О проекте
│   └── index.vue # Главная страница. Пока что импортит MainViz
├── plugins
│   ├── README.md
│   └── dataLoaderInject.js # Глобальный инжект DataLoader объекта (this.$dataloader)
├── scripts
│   ├── DataLoader.js # Dev и Prod DataLoader
│   └── placeholder_data
├── static
│   ├── README.md
│   ├── favicon.ico
│   ├── icon.png
│   └── sw.js
└── store
    └── README.md
```

## Документация
* [BootstrapVue](https://bootstrap-vue.js.org/docs/components) - библиотека компонентов
* [Bootstrap](https://getbootstrap.com/docs/4.4/getting-started/introduction/) - стили
* [Vue.js](https://vuejs.org/) - фреймворк для написания компонентов
* [Nuxt.js](https://nuxtjs.org/)

# Backend
TODO

Желательно чтобы уже был готов [питоновый DataLoader](https://trello.com/c/96T7E5yM/91-%D0%BD%D0%B0%D0%BF%D0%B8%D1%81%D0%B0%D1%82%D1%8C-dataloader).