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
import { useTranslation } from 'react-i18next';

const SELFCARE_GUIDE_URL = 'https://adn.systems/selfcare/';
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
} as const;

type FaqImageKey = keyof typeof IMG_FAQ;

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

export default function Help() {
  const { t } = useTranslation();

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} color="text.primary" sx={{ mb: 2 }}>
        {t('help_title', { defaultValue: 'Help' })}
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 2 }}>
        {t('help_subtitle', { defaultValue: 'ADN SelfCare – Frequently asked questions and setup guide.' })}
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
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
        {t('help_faq', { defaultValue: 'FAQ' })}
      </Typography>

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={500}>{t('help_faq0_q', { defaultValue: 'What is ADN SelfCare?' })}</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" paragraph>
            {t('help_faq0_a', { defaultValue: 'ADN SelfCare lets you create and manage your "DMR-ID secure" password. This password protects your DMR ID when connecting to ADN Systems (repeaters, hotspots, bridges). Use the SelfCare link to set it.' })}
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion defaultExpanded>
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
    </Box>
  );
}
