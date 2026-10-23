// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

import { themes } from 'prism-react-renderer';
import { hagilightDocusaurus } from '@hagicode/hagilight-docusaurus';

const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

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
      "@easyops-cn/docusaurus-search-local",
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

  plugins: [
    hagilightDocusaurus({
      links: {
        siteId: 'newbe-blog',
        extraLinks: {
          quick: [
            { id: 'newbe-home', label: 'Newbe 博客', href: '/', external: false },
            { id: 'newbe-focus', label: '重点关注', href: '/links', external: false },
            { id: 'newbe-privacy', label: '隐私策略', href: '/privacy', external: false },
          ],
          community: [
            { id: 'steam', label: 'Steam', href: 'https://store.steampowered.com/app/4625540/Hagicode/', external: true },
          ],
          // Genuine site-specific extras: none of these four are in hagilight's bundled
          // related-sites data (verified against @hagicode/hagilight-core 0.15.1), so keep them.
          relatedSites: [
            { id: 'masuit', name: '懒得勤快', url: 'https://masuit.org' },
            { id: 'whuanle', name: '面向云技术架构 - 痴者工良', url: 'https://www.whuanle.cn/' },
            { id: 'eventhorizon', name: '黑洞视界', url: 'https://www.cnblogs.com/eventhorizon/' },
            { id: 'alexinea', name: 'Alex Lewis', url: 'https://alexinea.com/' },
          ],
        },
      },
      languageSelector: { enabled: false },
    }),
  ],

  scripts: [
    {
      src: 'https://sdk.jinrishici.com/v2/browser/jinrishici.js',
      charset: 'utf-8',
    },
    {
      src: 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4138796439241260',
      async: true,
      crossorigin: 'anonymous',
    },
  ],

  headTags: [
    {
      tagName: 'script',
      attributes: {},
      innerHTML: `
var _mtac = {};
(function () {
  var mta = document.createElement('script');
  mta.src = '//pingjs.qq.com/h5/stats.js?v2.0.4';
  mta.setAttribute('name', 'MTAH5');
  mta.setAttribute('sid', '500724123');

  var s = document.getElementsByTagName('script')[0];
  s.parentNode.insertBefore(mta, s);
})();


(function(c,l,a,r,i,t,y){
  c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
  t=l.createElement(r);t.async=1;t.src='https://www.clarity.ms/tag/'+i;
  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, 'clarity', 'script', 'j15shshi6c');
      `,
    },
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
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
          customCss: './src/css/custom.css',
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
      prism: {
        additionalLanguages: ['powershell','csharp','java','sql'],
        theme: darkCodeTheme,
        darkTheme: darkCodeTheme,
      }
    }),
};

export default config;
