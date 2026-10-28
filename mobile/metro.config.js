const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Add explicit resolver settings
config.resolver.extraNodeModules = {
  ...config.resolver.extraNodeModules,
  expo: require.resolve('expo'),
};

// Ensure source extensions are properly set
config.resolver.sourceExts = ['js', 'jsx', 'json', 'ts', 'tsx', 'cjs', 'mjs'];

module.exports = config;
