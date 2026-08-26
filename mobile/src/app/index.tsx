import { useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useLanguage, type LanguageCode } from '../i18n';
import { colors, fontSize, radius, spacing } from '../theme/tokens';

/**
 * Language selection — the first screen. Hindi first by default.
 * (Persistence lands with the auth phase; Phase 0 keeps this stateless.)
 */
export default function LanguageSelect() {
  const { setLang } = useLanguage();
  const router = useRouter();

  const choose = (code: LanguageCode) => {
    setLang(code);
    router.replace('/(tabs)/prices');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>अपनी भाषा चुनें</Text>
      <Text style={styles.subtitle}>Choose your language</Text>

      <Pressable style={styles.button} onPress={() => choose('hi')}>
        <Text style={styles.buttonText}>हिंदी</Text>
      </Pressable>
      <Pressable style={styles.button} onPress={() => choose('en')}>
        <Text style={styles.buttonText}>English</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.lg,
    gap: spacing.md,
  },
  title: { color: '#FFFFFF', fontSize: fontSize.title + 6, fontWeight: '700' },
  subtitle: { color: colors.primaryLight, fontSize: fontSize.body },
  button: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl + spacing.md,
    minWidth: 220,
    alignItems: 'center',
  },
  buttonText: { color: colors.primary, fontSize: fontSize.body + 2, fontWeight: '600' },
});
