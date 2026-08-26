import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useMemo, useState } from 'react';
import { LanguageContext, type LanguageCode } from '../i18n';
import { colors } from '../theme/tokens';

export default function RootLayout() {
  const [lang, setLang] = useState<LanguageCode>('hi');
  const value = useMemo(() => ({ lang, setLang }), [lang]);

  return (
    <LanguageContext.Provider value={value}>
      <StatusBar style="light" />
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="(tabs)" />
      </Stack>
    </LanguageContext.Provider>
  );
}
