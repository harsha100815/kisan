import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { api } from '../../api/client';
import { SUPPORTED_LANGUAGES, useLanguage, useT } from '../../i18n';
import { colors, fontSize, radius, spacing } from '../../theme/tokens';

/** Settings: live server status + language switch. Alerts/help land later. */
export default function MoreScreen() {
  const t = useT();
  const { lang, setLang } = useLanguage();
  const [server, setServer] = useState<'checking' | 'ok' | 'down'>('checking');

  useEffect(() => {
    let alive = true;
    api.health()
      .then(() => alive && setServer('ok'))
      .catch(() => alive && setServer('down'));
    return () => {
      alive = false;
    };
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('more.title')}</Text>

      <View style={styles.statusRow}>
        <View style={[styles.dot, server === 'ok' && styles.dotOk, server === 'down' && styles.dotDown]} />
        <Text style={styles.statusText}>
          {server === 'ok' ? t('more.server_ok') : server === 'down' ? t('more.server_down') : '…'}
        </Text>
      </View>

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
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: colors.border,
  },
  dot: { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.textMuted },
  dotOk: { backgroundColor: '#2E7D32' },
  dotDown: { backgroundColor: colors.danger },
  statusText: { fontSize: fontSize.body, color: colors.text },
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
