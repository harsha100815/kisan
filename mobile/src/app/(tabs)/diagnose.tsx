import { StyleSheet, Text, View } from 'react-native';
import { useT } from '../../i18n';
import { colors, fontSize, radius, spacing } from '../../theme/tokens';

/**
 * Placeholder for the photo-diagnosis flow (Phase 1+).
 * Copy already reflects the uncertainty policy: results are always preliminary.
 */
export default function DiagnoseScreen() {
  const t = useT();
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('diag.title')}</Text>
      <View style={styles.card}>
        <Text style={styles.cardText}>{t('diag.take_photo')}</Text>
        <Text style={styles.disclaimer}>{t('diag.disclaimer.not_guaranteed')}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: spacing.md, gap: spacing.md },
  title: { fontSize: fontSize.title, fontWeight: '700', color: colors.text },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.lg,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: colors.border,
    gap: spacing.sm,
  },
  cardText: { fontSize: fontSize.body, color: colors.text },
  disclaimer: { fontSize: fontSize.small, color: colors.danger },
});
