const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Let Metro compile the canonical locales from ../../shared (monorepo support).
config.watchFolders = [`${__dirname}/../shared`];

module.exports = config;
