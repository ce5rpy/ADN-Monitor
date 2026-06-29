/*
 * ADN Monitor - Dashboard and backend for ADN Systems.
 * Copyright (C) 2026  Rodrigo Pérez, CE5RPY <ce5rpy@qmd.cl>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Derived from: FDMR Monitor (OA4DOA, https://github.com/yuvelq/FDMR-Monitor);
 * HBMonv2 (SP2ONG, https://github.com/sp2ong/HBMonv2);
 * hbmonitor3 (KC1AWV, https://github.com/kc1awv/hbmonitor3);
 * HBmonitor (Cortney T. Buffington, N0MJS, Copyright (C) 2013-2018).
 * Original works and this derivative are under GPLv3.
 */

import {
  Box,
  Typography,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const SELFCARE_GUIDE_URL = 'https://adn.systems/how-to-selfcare/';
const SELFCARE_VIDEO_URL = 'https://www.youtube.com/watch?v=OMQOuqtGCMc';
const SELFCARE_DIRECT_URL = 'https://selfcare.adn.systems/';

/** Local FAQ image paths. Step 1–5: public/img/faq. Password hint: public/img/help. */
const IMG_FAQ = {
  step1: '/img/faq/selfcare1.png',
  step2: '/img/faq/selfcare2.png',
  step3: '/img/faq/selfcare3.png',
  step4: '/img/faq/selfcare4.png',
  step5: '/img/faq/selfcare5.png',
  pista: '/img/faq/passw0rd.jpg',
  pistarPass: '/img/pi-star_pass.png',
  wpsdPass: '/img/wpsd_pass.png',
  pistarOptions: '/img/pi-star_options.png',
  wpsdOptions: '/img/wpsd_options.png',
} as const;

type FaqImageKey = keyof typeof IMG_FAQ;

function FaqBulletList({ keys }: { keys: readonly string[] }) {
  const { t } = useTranslation();
  return (
    <Box component="ul" sx={{ pl: 2.5, my: 1, '& li': { mb: 0.5 } }}>
      {keys.map((key) => (
        <li key={key}>
          <Typography variant="body2">{t(key)}</Typography>
        </li>
      ))}
    </Box>
  );
}

function FaqCode({ textKey }: { textKey: string }) {
  const { t } = useTranslation();
  return (
    <Box
      component="pre"
      sx={{
        p: 1.5,
        my: 1.5,
        bgcolor: 'action.hover',
        borderRadius: 1,
        fontSize: '0.8rem',
        overflow: 'auto',
        border: 1,
        borderColor: 'divider',
      }}
    >
      {t(textKey)}
    </Box>
  );
}

function FaqImage({ name, alt }: { name: FaqImageKey; alt: string }) {
  return (
    <Box sx={{ my: 1.5, textAlign: 'center' }}>
      <Box
        component="img"
        src={IMG_FAQ[name]}
        alt={alt}
        sx={{ maxWidth: '100%', height: 'auto', borderRadius: 1, border: 1, borderColor: 'divider' }}
      />
    </Box>
  );
}

function OptionsFormatSection() {
  const { t } = useTranslation();
  return (
    <>
      <Typography variant="body2" paragraph>
        {t('help_options_format_intro', {
          defaultValue:
            'The OPTIONS line is a semicolon-separated list of KEY=value pairs (Homebrew format). The server stores it for your hotspot and applies it on registration.',
        })}
      </Typography>
      <Typography variant="body2" fontWeight={600}>
        {t('help_ss_options_a2', {
          defaultValue: 'Common keys:',
        })}
      </Typography>
      <FaqBulletList
        keys={[
          'help_ss_options_li1',
          'help_ss_options_li2',
          'help_ss_options_li3',
          'help_ss_options_li4',
        ]}
      />
      <Typography variant="body2" fontWeight={600}>
        {t('help_ss_options_example_label', { defaultValue: 'Example' })}
      </Typography>
      <FaqCode textKey="help_ss_options_example" />
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        {t('help_options_format_routing', {
          defaultValue:
            'You can edit this line in Self Service (if your network enables it) or paste it directly into your hotspot software — see the next sections.',
        })}
      </Typography>
    </>
  );
}

export default function Help() {
  const { t } = useTranslation();

  return (
    <Box>
      <Paper
        variant="outlined"
        sx={{
          p: 1.5,
          mb: 1.5,
          bgcolor: 'background.paper',
          boxShadow: (theme) => theme.palette.mode === 'dark' ? 'none' : '0 1px 3px rgba(0,0,0,0.08)',
        }}
      >
        <Typography variant="subtitle1" fontWeight={700} color="text.primary" sx={{ mb: 0.5 }}>
          {t('help_title', { defaultValue: 'Help' })}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {t('help_subtitle', { defaultValue: 'SelfCare, talkgroups, OPTIONS, Talker Alias, and hotspot setup — frequently asked questions.' })}
        </Typography>
      </Paper>

      <Paper sx={{ p: { xs: 1.5, sm: 2 }, mb: 3 }}>
        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
          {t('help_guide', { defaultValue: 'Full guide and video' })}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {t('help_guide_desc', { defaultValue: 'Step-by-step instructions on adn.systems. Video tutorial (Spanish) from NetDigital Venezuela.' })}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
          {t('help_video_spanish', { defaultValue: 'The video is in Spanish.' })}
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Button
            component="a"
            href={SELFCARE_GUIDE_URL}
            target="_blank"
            rel="noopener noreferrer"
            variant="outlined"
            size="small"
            endIcon={<OpenInNewIcon />}
          >
            {t('help_open_guide', { defaultValue: 'Open SelfCare guide (adn.systems)' })}
          </Button>
          <Button
            component="a"
            href={SELFCARE_VIDEO_URL}
            target="_blank"
            rel="noopener noreferrer"
            variant="outlined"
            size="small"
            color="secondary"
            endIcon={<PlayCircleOutlineIcon />}
          >
            {t('help_watch_video', { defaultValue: 'Watch video' })}
          </Button>
        </Box>
      </Paper>

      <Typography variant="subtitle2" fontWeight={600} color="text.primary" sx={{ mb: 1.5 }}>
        {t('help_faq_selfcare_section', { defaultValue: 'SelfCare & password' })}
      </Typography>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>{t('help_faq0_q', { defaultValue: 'What is ADN SelfCare?' })}</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_faq0_a', { defaultValue: 'ADN SelfCare lets you create and manage your "DMR-ID secure" password. This password protects your DMR ID when connecting to ADN Systems (repeaters, hotspots, bridges). Use the SelfCare link to set it.' })}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>{t('help_faq_step_title', { defaultValue: 'Step by step' })}</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Button
            component="a"
            href={SELFCARE_DIRECT_URL}
            target="_blank"
            rel="noopener noreferrer"
            variant="outlined"
            size="small"
            sx={{ mb: 1 }}
            endIcon={<OpenInNewIcon />}
          >          
            {t('help_faq1_link', { defaultValue: 'Open SelfCare' })}
          </Button>
          <Typography variant="body2" paragraph fontWeight={600}>
            1. {t('help_step2_title', { defaultValue: 'Click on the button "Access / Set / Recover Password".' })}
          </Typography>
          
          <FaqImage name="step1" alt={t('help_img_step1', { defaultValue: 'Selfcare menu and Access / Set / Recover Password button' })} />

          <Typography variant="body2" paragraph fontWeight={600} sx={{ mt: 2 }}>
            2. {t('help_step3_title', { defaultValue: 'Enter your callsign and email address registered on RadioID.net, and click "Verify Identity". You will receive a link in your email to access the selfcare panel.' })}
          </Typography>
          <FaqImage name="step2" alt={t('help_img_step2', { defaultValue: 'Form: callsign, email, Verify Identity button' })} />

          <Typography variant="body2" paragraph fontWeight={600} sx={{ mt: 2 }}>
            3. {t('help_step3_caption', { defaultValue: 'You will receive a link in your email. In the selfcare panel:' })}
          </Typography>
          <FaqImage name="step3" alt={t('help_img_step3', { defaultValue: 'Verification link sent' })} />

          <Typography variant="body2" paragraph fontWeight={600} sx={{ mt: 2 }}>
            4. {t('help_step4_title', { defaultValue: 'If you have more than one ID registered to your callsign, select the ID for which you want to set the hotspot password.' })}
          </Typography>
          <Box component="ul" sx={{ pl: 2.5, '& li': { mb: 0.5 } }}>
            <li><Typography variant="body2">{t('help_step4_li1', { defaultValue: 'Enter your new hotspot password.' })}</Typography></li>
            <li><Typography variant="body2">{t('help_step4_li2', { defaultValue: 'Confirm your new hotspot password.' })}</Typography></li>
            <li><Typography variant="body2">{t('help_step4_li3', { defaultValue: 'Click the "Set Password" button.' })}</Typography></li>
          </Box>
          <Typography variant="body2" paragraph>
            {t('help_step4_email', { defaultValue: 'You will receive a confirmation email with the new password you must use to connect your hotspots.' })}
          </Typography>
          <FaqImage name="step4" alt={t('help_img_step4', { defaultValue: 'Select ID and set password' })} />
          <FaqImage name="step5" alt={t('help_img_step5', { defaultValue: 'Password set confirmation' })} />

          <Typography variant="body2" paragraph fontWeight={600} sx={{ mt: 2 }}>
            5. {t('help_step5_title', { defaultValue: 'Configure your hotspot to use your new password' })}
          </Typography>
          <Typography variant="body2" component="span" fontWeight={600}>
            {t('help_step5a_label', { defaultValue: '5A. Pi-Star' })}
          </Typography>
          <Box component="ul" sx={{ pl: 2.5, mt: 0.5, '& li': { mb: 0.5 } }}>
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <li key={i}>
                <Typography variant="body2">{t(`help_step5a_li${i}` as const, { defaultValue: ['Connect to your Pi-Star Dashboard.', 'Configuration → Expert → MMDVMHost.', 'Scroll down to "DMR Network" (Address: xxxx.adn.systems).', 'Type your new password in the "Password" field.', 'Click "Apply Changes", wait, verify connection.', 'Reboot hotspot if connection does not work.'][i - 1] })}</Typography>
              </li>
            ))}
          </Box>
          <Typography variant="body2" component="span" fontWeight={600} sx={{ display: 'block', mt: 1.5 }}>
            {t('help_step5b_label', { defaultValue: '5B. WPSD' })}
          </Typography>
          <Box component="ul" sx={{ pl: 2.5, mt: 0.5, '& li': { mb: 0.5 } }}>
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <li key={i}>
                <Typography variant="body2">{t(`help_step5b_li${i}` as const, { defaultValue: ['Connect to your WPSD Dashboard.', 'Admin → Advanced → Quick Editors → DMR → DMR Gateway.', 'Scroll down to "DMR Network" (Address: xxxx.adn.systems).', 'Type your new password in the "Password" field.', 'Click "Apply Changes", wait, verify connection.', 'Reboot hotspot if connection does not work.'][i - 1] })}</Typography>
              </li>
            ))}
          </Box>
          <FaqImage name="pista" alt={t('help_img_pista', { defaultValue: 'Password field in DMR Network (Pi-Star / WPSD)' })} />
          <Typography variant="body2" paragraph sx={{ mt: 2 }}>
            {t('help_step_done', { defaultValue: 'Your new secure password will be ready to connect successfully to the ADN Systems DMR network.' })}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>{t('help_faq4_q', { defaultValue: 'Is the DMR-ID secure password optional?' })}</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_faq4_a1', { defaultValue: 'Yes. It is optional. Users can choose whether to create it or not. If you do not create it, nothing changes. If you do create it, you must then use it in every client or device you use to connect to ADN Systems.' })}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>{t('help_faq5_q', { defaultValue: 'Where do I need to enter the password?' })}</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_faq5_a1', { defaultValue: 'If you create a DMR-ID secure password, you must enter it in all the software or devices you use to connect to ADN Systems. For example:' })}
          </Typography>
          <Box component="ul" sx={{ pl: 2.5, '& li': { mb: 0.5 } }}>
            <li><Typography variant="body2">DroidStar</Typography></li>
            <li><Typography variant="body2">DudeStar</Typography></li>
            <li><Typography variant="body2">BlueDV</Typography></li>
            <li><Typography variant="body2">Win-ADER</Typography></li>
            <li><Typography variant="body2">DVSwitch</Typography></li>
            <li><Typography variant="body2">Pi-Star</Typography></li>
            <li><Typography variant="body2">WPSD</Typography></li>
            <li><Typography variant="body2">Zum Spot</Typography></li>
            <li><Typography variant="body2">{t('help_faq5_etc', { defaultValue: '… and similar clients.' })}</Typography></li>
          </Box>
          <Typography variant="body2" paragraph>
            {t('help_faq5_a2', { defaultValue: 'At present, many of these programs do not yet have a dedicated field for this password. However, there are ways to enter it in most of them. Efforts are being made so that in the near future this option is visible in the main clients.' })}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>{t('help_faq6_q', { defaultValue: 'My client has no field for the password. What can I do?' })}</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_faq6_a1', { defaultValue: 'Many programs do not yet have a dedicated field for the DMR-ID secure password. There are workarounds to enter it in most of them. Efforts are underway so that in the near future this option is visible in the main clients.' })}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Typography variant="subtitle2" fontWeight={600} color="text.primary" sx={{ mt: 3, mb: 1.5 }}>
        {t('help_faq_tg_section', { defaultValue: 'Talkgroups & hotspot options' })}
      </Typography>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>
            {t('help_options_format_q', { defaultValue: 'OPTIONS line (reference)' })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <OptionsFormatSection />
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>
            {t('help_ss_configure_q', { defaultValue: 'Configure OPTIONS with Self Service' })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_ss_options_a1', {
              defaultValue:
                'If your network enables it, the Self Service page lets you log in and edit your hotspot preferences without asking a sysop. Changes are stored as an OPTIONS line and pushed to the ADN server, which updates your hotspot registration.',
            })}
          </Typography>

          <Typography variant="body2" fontWeight={600} sx={{ mt: 1 }}>
            {t('help_ss_login_title', { defaultValue: 'Access Self Service' })}
          </Typography>
          <FaqBulletList
            keys={[
              'help_ss_login_li1',
              'help_ss_login_li2',
              'help_ss_login_li3',
            ]}
          />

          <Typography variant="body2" fontWeight={600} sx={{ mt: 2 }}>
            {t('help_ss_device_title', { defaultValue: 'Prepare your hotspot software' })}
          </Typography>
          <Typography variant="body2" paragraph>
            {t('help_ss_device_instruc', {
              defaultValue:
                'Clear any local OPTIONS on the hotspot and set only PASS=your_password in Pi-Star or WPSD. The server supplies the OPTIONS line after you save in Self Service.',
            })}
          </Typography>
          <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
            {t('sslog_pistar', { defaultValue: 'Pi-star:' })}
          </Typography>
          <FaqImage
            name="pistarPass"
            alt={t('help_ss_img_pistar_alt', { defaultValue: 'Pi-Star DMR Network Options and PASS field' })}
          />
          <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1, mt: 2 }}>
            {t('sslog_wpsd', { defaultValue: 'WPSD:' })}
          </Typography>
          <FaqImage
            name="wpsdPass"
            alt={t('help_ss_img_wpsd_alt', { defaultValue: 'WPSD DMR Gateway Options and PASS field' })}
          />

          <Typography variant="body2" fontWeight={600} sx={{ mt: 2 }}>
            {t('help_ss_configure_steps_title', { defaultValue: 'Edit and save in Self Service' })}
          </Typography>
          <FaqBulletList
            keys={[
              'help_ss_configure_li1',
              'help_ss_configure_li2',
              'help_ss_configure_li3',
            ]}
          />
          <Typography variant="body2" paragraph>
            {t('help_ss_options_calc', {
              defaultValue:
                'Use the Options Calculator in the menu to build the line, then paste it into Self Service.',
            })}
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            <Button component={Link} to="/self-service" variant="contained" size="small">
              {t('self_service', { defaultValue: 'Self Service' })}
            </Button>
            <Button component={Link} to="/calc" variant="outlined" size="small">
              {t('nav_calc', { defaultValue: 'Options Calculator' })}
            </Button>
          </Box>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>
            {t('help_options_manual_q', { defaultValue: 'Configure OPTIONS without Self Service' })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_options_manual_a1', {
              defaultValue:
                'If your network does not offer Self Service or you prefer not to use the dashboard, apply the OPTIONS line directly in your hotspot software.',
            })}
          </Typography>
          <FaqBulletList
            keys={[
              'help_options_manual_li1',
              'help_options_manual_li2',
            ]}
          />
          <Typography variant="body2" fontWeight={600} sx={{ mt: 1 }}>
            {t('help_options_manual_paste_title', { defaultValue: 'Where to paste the line' })}
          </Typography>
          <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1, mt: 1 }}>
            {t('sslog_pistar', { defaultValue: 'Pi-star:' })}
          </Typography>
          <FaqImage
            name="pistarOptions"
            alt={t('help_options_manual_img_pistar_alt', {
              defaultValue: 'Pi-Star: Options field in DMR Network (MMDVMHost)',
            })}
          />
          <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1, mt: 2 }}>
            {t('sslog_wpsd', { defaultValue: 'WPSD:' })}
          </Typography>
          <FaqImage
            name="wpsdOptions"
            alt={t('help_options_manual_img_wpsd_alt', {
              defaultValue: 'WPSD: Options field in DMR Gateway',
            })}
          />
          <Typography variant="body2" paragraph sx={{ mt: 1 }}>
            {t('help_options_manual_calc', {
              defaultValue:
                'Build the line with the Options Calculator, copy it, and paste it into the hotspot Options field.',
            })}
          </Typography>
          <Button component={Link} to="/calc" variant="outlined" size="small">
            {t('nav_calc', { defaultValue: 'Options Calculator' })}
          </Button>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>
            {t('help_static_dynamic_q', { defaultValue: 'Static vs dynamic talkgroups' })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" fontWeight={600} gutterBottom>
            {t('help_static_dynamic_static_title', { defaultValue: 'Static talkgroups' })}
          </Typography>
          <Typography variant="body2" paragraph>
            {t('help_static_dynamic_static_body', {
              defaultValue:
                'Listed in your OPTIONS as TS1= or TS2= (comma-separated TG numbers). They are always available on your hotspot and appear as fixed chips on the dashboard. Configure them in Self Service or in your hotspot OPTIONS field.',
            })}
          </Typography>
          <Typography variant="body2" fontWeight={600} gutterBottom>
            {t('help_static_dynamic_dynamic_title', { defaultValue: 'Dynamic (user-activated) talkgroups' })}
          </Typography>
          <Typography variant="body2" paragraph>
            {t('help_static_dynamic_dynamic_body', {
              defaultValue:
                'When you transmit to a talkgroup that is not in your static lists, the server opens a temporary bridge for your hotspot. These show as indigo chips on the dashboard. Since ADN server version 2.0.0, they can survive a hotspot reconnect.',
            })}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {t('help_static_dynamic_note', {
              defaultValue:
                'Network ACLs may block some TGs. Static lists define what your hotspot advertises; dynamic TGs are created when you actually key them.',
            })}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>
            {t('help_single_timer_q', { defaultValue: 'SINGLE=1 and TIMER (timeout)' })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" fontWeight={600} gutterBottom>
            {t('help_single_timer_single1_title', { defaultValue: 'SINGLE=1 (single dynamic TG per slot)' })}
          </Typography>
          <Typography variant="body2" paragraph>
            {t('help_single_timer_single1_body', {
              defaultValue:
                'Only one talkgroup per timeslot is selected for receive at a time. While you are not transmitting, you can hear traffic from all static TGs (in OPTIONS) and any dynamic TGs. When you transmit on one TG, that becomes the only TG you receive on that slot until the TIMER expires, you key TG 4000, or you transmit on a different TG.',
            })}
          </Typography>
          <Typography variant="body2" fontWeight={600} gutterBottom>
            {t('help_single_timer_single0_title', { defaultValue: 'SINGLE=0 (no receive exclusivity)' })}
          </Typography>
          <Typography variant="body2" paragraph>
            {t('help_single_timer_single0_body', {
              defaultValue:
                'There is no receive exclusivity: when the hotspot is idle (not transmitting), it receives traffic from all configured static and dynamic TGs. Several dynamic talkgroups can coexist on the same slot; the dashboard may show multiple indigo chips until you clear them with TG 4000.',
            })}
          </Typography>
          <Typography variant="body2" fontWeight={600} gutterBottom>
            {t('help_single_timer_timer_title', { defaultValue: 'TIMER (minutes)' })}
          </Typography>
          <Typography variant="body2" paragraph>
            {t('help_single_timer_timer_body', {
              defaultValue:
                'With SINGLE=1, how many minutes the selected dynamic TG stays active before the server removes it. In the Options Calculator, leave the timeout at 0 to omit TIMER and use the master default (DEFAULT_UA_TIMER). Do not write TIMER=0 in the OPTIONS line — the server treats that as no expiry, not the default.',
            })}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {t('help_single_timer_defaults', {
              defaultValue:
                'In the Options Calculator, “Server default” leaves SINGLE and TIMER to whatever your sysop configured on the master.',
            })}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>
            {t('help_tg4000_q', { defaultValue: 'TG 4000 — clear dynamic talkgroups' })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_tg4000_a1', {
              defaultValue:
                'TG 4000 is not a talkgroup for normal QSOs. It is a reset command for your hotspot: key TG 4000 briefly to clear all dynamic (user-activated) bridges on all timeslots.',
            })}
          </Typography>
          <FaqBulletList keys={['help_tg4000_li1', 'help_tg4000_li2', 'help_tg4000_li3']} />
        </AccordionDetails>
      </Accordion>

      <Typography variant="subtitle2" fontWeight={600} color="text.primary" sx={{ mt: 3, mb: 1.5 }}>
        {t('help_faq_display_section', { defaultValue: 'Radio display' })}
      </Typography>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>
            {t('help_ta_q', { defaultValue: 'Talker Alias (DMR)' })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_ta_a1', {
              defaultValue:
                'Talker Alias is a short text label (callsign, name, etc.) that some DMR radios can show on the display during a group call. It is carried inside the voice stream — not a talkgroup or service you dial.',
            })}
          </Typography>
          <Typography variant="body2" paragraph>
            {t('help_ta_a2', {
              defaultValue:
                'This is not the same as the name on the ADN Monitor dashboard or Last Heard log. Those come from the subscriber database. Talker Alias is meant for your radio screen (OLED, MD380tools, some Hytera models).',
            })}
          </Typography>
          <FaqBulletList keys={['help_ta_li1', 'help_ta_li2', 'help_ta_li3']} />
          <Typography variant="body2" color="text.secondary">
            {t('help_ta_note', {
              defaultValue:
                'Whether Talker Alias appears on bridged calls depends on your network operator. It is not configured from Self Service or the Options line — contact your sysop if you use a compatible radio and never see it.',
            })}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>
            {t('help_daprs_q', { defaultValue: 'D-APRS' })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_daprs_a1', {
              defaultValue:
                'D-APRS is the APRS gateway on the ADN network (position reports, messages, and related data over DMR). Your radio or DMR client must be set up to send APRS over DMR to the D-APRS talkgroup — not via the OPTIONS line on the server.',
            })}
          </Typography>
          <Typography variant="body2" paragraph>
            {t('help_daprs_a2', {
              defaultValue:
                'The default D-APRS talkgroup is 900999, unless your network administrator has configured a different TG in the server bridges.',
            })}
          </Typography>
          <Typography variant="body2" paragraph color="text.secondary">
            {t('help_daprs_a3', {
              defaultValue:
                'D-APRS is optional: each ADN server may have it enabled or not. Some networks do not offer the service — if yours does not, you will not see a D-APRS entry under Linked Systems → Bridges (IP).',
            })}
          </Typography>
          <FaqBulletList keys={['help_daprs_li1', 'help_daprs_li2']} />
          <Button component={Link} to="/systems" variant="outlined" size="small" sx={{ mt: 1 }}>
            {t('nav_lnksys', { defaultValue: 'Linked Systems' })}
          </Button>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>
            {t('help_echo_q', { defaultValue: 'Echo (parrot / playback)' })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_echo_a1', {
              defaultValue:
                'Echo records your group voice transmission and plays it back to you — useful to test audio, levels, and connectivity. Transmit on the echo talkgroup and you should hear your own recording shortly after.',
            })}
          </Typography>
          <Typography variant="body2" paragraph>
            {t('help_echo_a2', {
              defaultValue:
                'The default echo talkgroup is 9990, unless your network administrator has configured a different TG in the server bridges.',
            })}
          </Typography>
          <Typography variant="body2" paragraph color="text.secondary">
            {t('help_echo_a3', {
              defaultValue:
                'Echo is optional: each ADN server may have it enabled or not. Some networks do not offer the service — if yours does not, you will not see an ECHO entry under Linked Systems → Bridges (IP).',
            })}
          </Typography>
          <FaqBulletList keys={['help_echo_li1', 'help_echo_li2']} />
          <Button component={Link} to="/systems" variant="outlined" size="small" sx={{ mt: 1 }}>
            {t('nav_lnksys', { defaultValue: 'Linked Systems' })}
          </Button>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}
