// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;
const { resolveNewbeFooterLinks } = require('./footer-sites');

const default51LAId = 'L6b88a5yK4h2Xnci';
const la51Id = process.env.LI_51LA_ID || default51LAId;
const isProduction = process.env.NODE_ENV === 'production';
const is51LAEnabled =
  process.env.LI_51LA_ENABLED !== 'false' &&
  process.env.LI_51LA_ENABLED !== '0' &&
  isProduction;
const is51LADebug =
  process.env.LI_51LA_DEBUG === 'true' || process.env.LI_51LA_DEBUG === '1';

// Reverse the sidebar items ordering (including nested category items)
/**
 * @param {any[]} items
 * @returns {any[]}
 */
function reverseSidebarItems(items) {
  // Reverse items in categories
  const result = items.map((item) => {
    if (item.type === 'category') {
      if (item.label === '随笔') {
        item.items.reverse();
        return {...item, items: item.items};
      }else{
        return {...item, items: reverseSidebarItems(item.items)};
      }
    }
    return item;
  });
  return result;
}


/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'newbe',
  tagline: 'Now, everyone will be excellent!',
  favicon: 'images/icons/favicon.ico',

  // Set the production url of your site here
  url: 'https://newbe.hagicode.com/',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  // organizationName: 'facebook', // Usually your GitHub org/user name.
  // projectName: 'docusaurus', // Usually your repo name.

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'zh',
    locales: ['zh'],
  },

  themes: [
    // ... Your other themes.
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      // /** @type {import("@easyops-cn/docusaurus-search-local").PluginOptions} */
      ({
        // ... Your options.
        // `hashed` is recommended as long-term-cache of index file is possible.
        hashed: true,
        indexBlog: false,
        docsRouteBasePath: '/',

        // For Docs using Chinese, The `language` is recommended to set to:
        // ```
        language: ["en", "zh"],
        // ```
      }),
    ],
  ],

  headTags: is51LAEnabled
    ? [
        {
          tagName: 'script',
          attributes: {
            charset: 'UTF-8',
            id: 'LA_COLLECT',
            src: '//sdk.51.la/js-sdk-pro.min.js',
          },
        },
        {
          tagName: 'script',
          attributes: {},
          innerHTML: `
if (typeof LA !== 'undefined' && typeof LA.init === 'function') {
  LA.init({id:'${la51Id}',ck:'${la51Id}',autoTrack:true,hashMode:true,screenRecord:true});
}
${is51LADebug ? `console.log('[51LA Analytics] Enabled:', true, 'id:', '***${la51Id.slice(-4)}');` : ''}
          `.trim(),
        },
      ]
    : [],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          routeBasePath: '/',
          async sidebarItemsGenerator({defaultSidebarItemsGenerator, ...args}) {
            const sidebarItems = await defaultSidebarItemsGenerator(args);
            return reverseSidebarItems(sidebarItems);
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          // editUrl:
          //   'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: false,
        // blog: {
        //   showReadingTime: true,
        //   // Please change this to your repo.
        //   // Remove this to remove the "edit this page" links.
        //   // editUrl:
        //   //   'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        // },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        gtag: {
          trackingID: 'G-V1E9RK7C36',
          anonymizeIP: true,
        },
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
          ignorePatterns: ['/tags/**'],
          filename: 'sitemap.xml',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: '',
        logo: {
          alt: 'Newbe Logo',
          src: 'images/logo/main-logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: '博客',
          },
          {
            label: 'QQ 群 610394020',
            href: 'https://jq.qq.com/?_wv=1027&k=3PUr2L5i',
            position: 'left',
          },
          {
            href: 'https://github.com/newbe36524',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: '博客',
                to: '/',
              },
              {
                label: '重点关注',
                to: '/links',
              },
              {
                label: '隐私策略',
                to: '/privacy',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'QQ 群 610394020',
                href: 'https://jq.qq.com/?_wv=1027&k=3PUr2L5i',
              },
              {
                label: 'Steam',
                href: 'https://store.steampowered.com/app/4625540/Hagicode/',
              },
              // {
              //   label: 'Discord',
              //   href: 'https://discordapp.com/invite/docusaurus',
              // },
              // {
              //   label: 'Twitter',
              //   href: 'https://twitter.com/docusaurus',
              // },
            ],
          },
          {
            title: '友情链接',
            items: [
              {
                label: '懒得勤快',
                to: 'https://masuit.org'
              },
              {
                label: '面向云技术架构 - 痴者工良',
                to: 'https://www.whuanle.cn/'
              },
              {
                label: '黑洞视界',
                to: 'https://www.cnblogs.com/eventhorizon/'
              },
              {
                label: 'Alex Lewis',
                to: 'https://alexinea.com/'
              },
            ],
          },
          {
            title: 'Hagicode',
            items: resolveNewbeFooterLinks().map((link) => ({
              label: `${link.title} · ${link.description}`,
              href: link.href,
            })),
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} newbe36524, Built with Docusaurus.`,
      },
      prism: {
        additionalLanguages: ['powershell','csharp','java','sql'],
        theme: darkCodeTheme,
        darkTheme: darkCodeTheme,
      }
    }),
};

module.exports = config;
