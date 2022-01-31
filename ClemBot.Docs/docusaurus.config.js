// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/dracula");

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "ClemBot",
  tagline: "Modular and Configurable Discord Bot",
  url: "https://clembotdocs.netlify.app",
  baseUrl: "/",
  onBrokenLinks: "log",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/ClemBotLogo.svg",
  organizationName: "ClemBotProject", // Usually your GitHub org/user name.
  projectName: "ClemBot", // Usually your repo name.
  plugins: ['docusaurus-plugin-sass'],

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: "/", // Serve the docs at the site's root
          /* other docs plugin options */
        },
        blog: false, // Optional: disable the blog plugin
        theme: {
          customCss: [require.resolve("./src/css/custom.scss")],
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      defaultMode: "dark",
      navbar: {
        title: "ClemBot Wiki",
        logo: {
          alt: "My Site Logo",
          src: "img/ClemBotLogo.svg",
        },
        items: [
          {
            to: "https://github.com/ClemBotProject/ClemBot",
            className: 'header-github-link',
            position: "right",
          },
        ],
      },

      footer: {
        style: "dark",
        links: [
          {
            title: "Docs",
            items: [
              {
                label: "Tutorial",
                to: "/docs/intro",
              },
            ],
          },
          {
            title: "Community",
            items: [
              {
                label: "Discord",
                href: "https://discord.gg/mhrVuyh",
              },
              {
                label: "GitHub",
                href: "https://github.com/ClemBotProject/ClemBot",
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} ClemBot, Inc. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};

module.exports = config;
