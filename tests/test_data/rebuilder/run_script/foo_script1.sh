#!/bin/bash
echo FUCK $(env | grep FOO_VAR)
mkdir -p ${REBUILD_STAGE_PREFIX_DIR}/bin
cat << EOF > ${REBUILD_STAGE_PREFIX_DIR}/bin/foo1.sh
#!/bin/bash
echo ${FOO_VAR}
EOF
chmod 755 ${REBUILD_STAGE_PREFIX_DIR}/bin/foo1.sh
