import { Tabs } from 'expo-router';
import { Text } from 'react-native';
import { useT } from '../../i18n';
import { colors, fontSize } from '../../theme/tokens';

function TabIcon({ glyph }: { glyph: string }) {
  return <Text style={{ fontSize: fontSize.title - 2 }}>{glyph}</Text>;
}

/** Bottom navigation: भाव · फसल जाँच · सलाह · और — prices is the default tab. */
export default function TabsLayout() {
  const t = useT();
  return (
    <Tabs
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: colors.primary },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: { fontSize: fontSize.body + 2 },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarLabelStyle: { fontSize: fontSize.small },
      }}
    >
      <Tabs.Screen
        name="prices"
        options={{ title: t('tabs.prices'), tabBarIcon: () => <TabIcon glyph="🌾" /> }}
      />
      <Tabs.Screen
        name="diagnose"
        options={{ title: t('tabs.diagnose'), tabBarIcon: () => <TabIcon glyph="📷" /> }}
      />
      <Tabs.Screen
        name="advisory"
        options={{ title: t('tabs.advisory'), tabBarIcon: () => <TabIcon glyph="📰" /> }}
      />
      <Tabs.Screen
        name="more"
        options={{ title: t('tabs.more'), tabBarIcon: () => <TabIcon glyph="☰" /> }}
      />
    </Tabs>
  );
}
