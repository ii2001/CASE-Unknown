import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import vue from 'eslint-plugin-vue'

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...vue.configs['flat/recommended'],
  { languageOptions: { globals: { fetch: 'readonly', EventSource: 'readonly', crypto: 'readonly' } } },
  { files: ['**/*.vue'], languageOptions: { parserOptions: { parser: tseslint.parser } }, rules: { 'vue/multi-word-component-names': 'off' } },
  { ignores: ['dist'] },
)
