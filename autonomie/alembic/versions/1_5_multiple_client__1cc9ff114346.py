"""1.5 Project : Multiple clients per project

Revision ID: 1cc9ff114346
Revises: 70853b55768c
Create Date: 2012-12-20 10:22:18.381606

"""

# revision identifiers, used by Alembic.
revision = '1cc9ff114346'
down_revision = '70853b55768c'

from alembic import op
import sqlalchemy as sa
from autonomie.models import DBSESSION

TABLENAMES = ('estimation', 'invoice', 'cancelinvoice')

def purge_line_type(factory):
    for line in factory.query():
        if line.task is None:
            DBSESSION().delete(line)

def upgrade():
    from autonomie.models.project import Project
    from autonomie.models.client import Client

    for proj in DBSESSION().query(Project):
        try:
            client = Client.get(proj.client_id)
            if client is not None:
                proj.clients.append(client)
                DBSESSION().merge(proj)
        except:
            continue

    # Adding foreign keys constraints to existing tables
    # First removing wrong references
    from autonomie.models.task import EstimationLine
    from autonomie.models.task import PaymentLine
    from autonomie.models.task import InvoiceLine
    from autonomie.models.task import CancelInvoiceLine

    for i in (EstimationLine, PaymentLine, InvoiceLine, CancelInvoiceLine):
        purge_line_type(i)

    # Adding the keys
    for i in TABLENAMES:
        op.create_foreign_key("fk_%s" % i, "%s_line" % i, i,
            ['task_id'], ['id'], ondelete="CASCADE")
    op.create_foreign_key("fk_estimation_payment", "estimation_payment",
            "estimation", ['task_id'], ['id'], ondelete="CASCADE")


def downgrade():
    op.execute("DELETE from project_client;")
    for i in TABLENAMES:
        op.execute("alter table %s_line drop foreign key fk_%s;" % (i,i))
    op.execute("alter table estimation_payment drop foreign key fk_estimation_payment")
