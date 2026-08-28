import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useT } from '../../i18n';
import { colors, fontSize, radius, spacing } from '../../theme/tokens';

const TIPS = [
  { title: 'advisory.tip1_title', body: 'advisory.tip1_body' },
  { title: 'advisory.tip2_title', body: 'advisory.tip2_body' },
  { title: 'advisory.tip3_title', body: 'advisory.tip3_body' },
] as const;

/** Season-wise advisory. Static localized tips for V1; personalized advice comes later. */
export default function AdvisoryScreen() {
  const t = useT();
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{t('advisory.title')}</Text>
      {TIPS.map(({ title, body }) => (
        <View key={title} style={styles.card}>
          <Text style={styles.cardTitle}>{t(title)}</Text>
          <Text style={styles.cardBody}>{t(body)}</Text>
        </View>
      ))}
      <Text style={styles.footnote}>{t('advisory.footnote')}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.md },
  title: { fontSize: fontSize.title, fontWeight: '700', color: colors.text },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.lg,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: colors.border,
    gap: spacing.xs,
  },
  cardTitle: { fontSize: fontSize.body + 1, fontWeight: '700', color: colors.primary },
  cardBody: { fontSize: fontSize.body, color: colors.text, lineHeight: fontSize.body + 6 },
  footnote: { fontSize: fontSize.small, color: colors.textMuted, textAlign: 'center', marginBottom: spacing.md },
});
