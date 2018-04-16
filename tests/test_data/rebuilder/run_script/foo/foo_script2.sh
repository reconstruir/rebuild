#!/bin/bash

mkdir -p ${REBUILD_STAGE_PREFIX_DIR}/bin
cat << EOF > ${REBUILD_STAGE_PREFIX_DIR}/bin/foo2.sh
#!/bin/bash
echo this is foo2.
EOF
chmod 755 ${REBUILD_STAGE_PREFIX_DIR}/bin/foo2.sh
