/*
 * This file is generated by jOOQ.
*/
package io.cattle.platform.core.model.tables;


import io.cattle.platform.core.model.CattleTable;
import io.cattle.platform.core.model.Keys;
import io.cattle.platform.core.model.tables.records.ProjectTemplateRecord;
import io.cattle.platform.db.jooq.converter.DataConverter;
import io.cattle.platform.db.jooq.converter.DateConverter;

import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Map;

import javax.annotation.Generated;

import org.jooq.Field;
import org.jooq.ForeignKey;
import org.jooq.Identity;
import org.jooq.Schema;
import org.jooq.Table;
import org.jooq.TableField;
import org.jooq.UniqueKey;
import org.jooq.impl.TableImpl;


/**
 * This class is generated by jOOQ.
 */
@Generated(
    value = {
        "http://www.jooq.org",
        "jOOQ version:3.9.3"
    },
    comments = "This class is generated by jOOQ"
)
@SuppressWarnings({ "all", "unchecked", "rawtypes" })
public class ProjectTemplateTable extends TableImpl<ProjectTemplateRecord> {

    private static final long serialVersionUID = 1491166651;

    /**
     * The reference instance of <code>cattle.project_template</code>
     */
    public static final ProjectTemplateTable PROJECT_TEMPLATE = new ProjectTemplateTable();

    /**
     * The class holding records for this type
     */
    @Override
    public Class<ProjectTemplateRecord> getRecordType() {
        return ProjectTemplateRecord.class;
    }

    /**
     * The column <code>cattle.project_template.id</code>.
     */
    public final TableField<ProjectTemplateRecord, Long> ID = createField("id", org.jooq.impl.SQLDataType.BIGINT.nullable(false), this, "");

    /**
     * The column <code>cattle.project_template.name</code>.
     */
    public final TableField<ProjectTemplateRecord, String> NAME = createField("name", org.jooq.impl.SQLDataType.VARCHAR.length(255), this, "");

    /**
     * The column <code>cattle.project_template.account_id</code>.
     */
    public final TableField<ProjectTemplateRecord, Long> ACCOUNT_ID = createField("account_id", org.jooq.impl.SQLDataType.BIGINT, this, "");

    /**
     * The column <code>cattle.project_template.kind</code>.
     */
    public final TableField<ProjectTemplateRecord, String> KIND = createField("kind", org.jooq.impl.SQLDataType.VARCHAR.length(255).nullable(false), this, "");

    /**
     * The column <code>cattle.project_template.uuid</code>.
     */
    public final TableField<ProjectTemplateRecord, String> UUID = createField("uuid", org.jooq.impl.SQLDataType.VARCHAR.length(128).nullable(false), this, "");

    /**
     * The column <code>cattle.project_template.description</code>.
     */
    public final TableField<ProjectTemplateRecord, String> DESCRIPTION = createField("description", org.jooq.impl.SQLDataType.VARCHAR.length(1024), this, "");

    /**
     * The column <code>cattle.project_template.state</code>.
     */
    public final TableField<ProjectTemplateRecord, String> STATE = createField("state", org.jooq.impl.SQLDataType.VARCHAR.length(128).nullable(false), this, "");

    /**
     * The column <code>cattle.project_template.created</code>.
     */
    public final TableField<ProjectTemplateRecord, Date> CREATED = createField("created", org.jooq.impl.SQLDataType.TIMESTAMP, this, "", new DateConverter());

    /**
     * The column <code>cattle.project_template.removed</code>.
     */
    public final TableField<ProjectTemplateRecord, Date> REMOVED = createField("removed", org.jooq.impl.SQLDataType.TIMESTAMP, this, "", new DateConverter());

    /**
     * The column <code>cattle.project_template.remove_time</code>.
     */
    public final TableField<ProjectTemplateRecord, Date> REMOVE_TIME = createField("remove_time", org.jooq.impl.SQLDataType.TIMESTAMP, this, "", new DateConverter());

    /**
     * The column <code>cattle.project_template.data</code>.
     */
    public final TableField<ProjectTemplateRecord, Map<String,Object>> DATA = createField("data", org.jooq.impl.SQLDataType.CLOB, this, "", new DataConverter());

    /**
     * The column <code>cattle.project_template.is_public</code>.
     */
    public final TableField<ProjectTemplateRecord, Boolean> IS_PUBLIC = createField("is_public", org.jooq.impl.SQLDataType.BIT.nullable(false).defaultValue(org.jooq.impl.DSL.inline("b'0'", org.jooq.impl.SQLDataType.BIT)), this, "");

    /**
     * The column <code>cattle.project_template.external_id</code>.
     */
    public final TableField<ProjectTemplateRecord, String> EXTERNAL_ID = createField("external_id", org.jooq.impl.SQLDataType.VARCHAR.length(255), this, "");

    /**
     * Create a <code>cattle.project_template</code> table reference
     */
    public ProjectTemplateTable() {
        this("project_template", null);
    }

    /**
     * Create an aliased <code>cattle.project_template</code> table reference
     */
    public ProjectTemplateTable(String alias) {
        this(alias, PROJECT_TEMPLATE);
    }

    private ProjectTemplateTable(String alias, Table<ProjectTemplateRecord> aliased) {
        this(alias, aliased, null);
    }

    private ProjectTemplateTable(String alias, Table<ProjectTemplateRecord> aliased, Field<?>[] parameters) {
        super(alias, null, aliased, parameters, "");
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public Schema getSchema() {
        return CattleTable.CATTLE;
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public Identity<ProjectTemplateRecord, Long> getIdentity() {
        return Keys.IDENTITY_PROJECT_TEMPLATE;
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public UniqueKey<ProjectTemplateRecord> getPrimaryKey() {
        return Keys.KEY_PROJECT_TEMPLATE_PRIMARY;
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public List<UniqueKey<ProjectTemplateRecord>> getKeys() {
        return Arrays.<UniqueKey<ProjectTemplateRecord>>asList(Keys.KEY_PROJECT_TEMPLATE_PRIMARY, Keys.KEY_PROJECT_TEMPLATE_IDX_PROJECT_TEMPLATE_UUID);
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public List<ForeignKey<ProjectTemplateRecord, ?>> getReferences() {
        return Arrays.<ForeignKey<ProjectTemplateRecord, ?>>asList(Keys.FK_PROJECT_TEMPLATE__ACCOUNT_ID);
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public ProjectTemplateTable as(String alias) {
        return new ProjectTemplateTable(alias, this);
    }

    /**
     * Rename this table
     */
    @Override
    public ProjectTemplateTable rename(String name) {
        return new ProjectTemplateTable(name, null);
    }
}
