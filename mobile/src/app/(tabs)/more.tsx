import { Pressable, StyleSheet, Text, View } from 'react-native';
import { SUPPORTED_LANGUAGES, useLanguage, useT } from '../../i18n';
import { colors, fontSize, radius, spacing } from '../../theme/tokens';

/** Settings placeholder: language switch works; alerts/help land later. */
export default function MoreScreen() {
  const t = useT();
  const { lang, setLang } = useLanguage();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('more.title')}</Text>
      <Text style={styles.section}>{t('more.language')}</Text>
      <View style={styles.row}>
        {SUPPORTED_LANGUAGES.map(({ code, nativeName }) => (
          <Pressable
            key={code}
            onPress={() => setLang(code)}
            style={[styles.chip, code === lang && styles.chipActive]}
          >
            <Text style={[styles.chipText, code === lang && styles.chipTextActive]}>
              {nativeName}
            </Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: spacing.md, gap: spacing.md },
  title: { fontSize: fontSize.title, fontWeight: '700', color: colors.text },
  section: { fontSize: fontSize.body, color: colors.textMuted, marginTop: spacing.sm },
  row: { flexDirection: 'row', gap: spacing.sm },
  chip: {
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { fontSize: fontSize.body, color: colors.text },
  chipTextActive: { color: '#FFFFFF' },
});
