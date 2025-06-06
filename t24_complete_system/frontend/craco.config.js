const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Add support for importing SVG files
      const svgRule = webpackConfig.module.rules.find(rule => rule.test?.test?.('.svg'));
      if (svgRule) {
        svgRule.exclude = /\.svg$/;
      }
      
      webpackConfig.module.rules.push({
        test: /\.svg$/,
        use: ['@svgr/webpack'],
      });
      
      return webpackConfig;
    },
  },
  style: {
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
      ],
    },
  },
};
