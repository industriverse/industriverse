/**
 * Universal Skin Module
 * 
 * This module serves as the entry point for the Universal Skin package.
 * It imports and exposes the main components of the Universal Skin UI system.
 */

import UniversalSkin from './UniversalSkin';
import UniversalSkinContainer from './UniversalSkinContainer';
import UniversalSkinApp from './UniversalSkinApp';
import { UniversalSkinProvider, useUniversalSkin } from './UniversalSkinContext';

export {
  UniversalSkin,
  UniversalSkinContainer,
  UniversalSkinApp,
  UniversalSkinProvider,
  useUniversalSkin
};

export default UniversalSkinApp;
