/** @odoo-module  **/

import { startWebClient } from '@web/start';
import { ProjectSharingWebClientEnterprise } from './project_sharing';
import { removeServices } from './remove_services';

removeServices();
startWebClient(ProjectSharingWebClientEnterprise);
