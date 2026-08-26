import { StyleSheet, Text, View } from 'react-native';
import { useT } from '../../i18n';
import { colors, fontSize, radius, spacing } from '../../theme/tokens';

/** Placeholder — real mandi prices land in Phase 1. */
export default function PricesScreen() {
  const t = useT();
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('prices.title')}</Text>
      <View style={styles.card}>
        <Text style={styles.cardText}>{t('prices.coming_soon')}</Text>
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
  },
  cardText: { fontSize: fontSize.body, color: colors.textMuted },
});
