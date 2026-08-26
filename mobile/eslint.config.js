// @ts-check
const { defineConfig } = require('eslint-config-expo/flat');

module.exports = defineConfig([
  {
    ignores: ['node_modules/', '.expo/'],
  },
  {
    files: ['**/*.{js,ts,tsx}'],
    rules: {},
  },
]);
