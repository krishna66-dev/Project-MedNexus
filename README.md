# Introduction

This website was built using Svelte. A web framework based on Vite.
Everything you need to build a Svelte project, powered by [`sv`](https://github.com/sveltejs/cli).

## Pre-requisites

- You will need Node.js and npm installed on your machine. NPM is included in most Node.js installations.
- An IDE or Text Editor. (Visual Studio Code, SublimeText, etc.)

## Developing

Once you've cloned this project, you may need to install dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.
> The current adapter being used is static. This is because the website is deployed on AWS Amplify, which needs a `index.html` file to redirect to.
> `amplify.yml` is the build configuration file that Amplify uses when building the websites, once changes are pushed and merged to main.

## Directories

The main directory to working in is `\src` this houses the wb structure (HTML, JS, CSS). The file that allows the content of the website to be displayed is `+page.svelte` in `\routes`. Pages themselves are stored in `\lib\sections`, `\lib\pages` and `\lib\layouts`.
Assets contains page/section assets. Scripts is used for any JS scripts such as page animation. Finally, styles is for any CSS styling to be applied. CSS styling is sometimes kept in section files to close couple them.

## lib folder understanding

src/lib directory. Anything inside this directory can be accessed by any module in src via the $lib alias.
https://svelte.dev/tutorial/kit/lib
