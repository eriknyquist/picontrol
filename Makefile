PROJECT_PATH := $(dir $(abspath $(MAKEFILE_LIST)))
PROTOBUF_SRC_DIR := $(PROJECT_PATH)picontrol/protobuf
PROTOBUF_OUT_DIR := $(PROTOBUF_SRC_DIR)/python

PROTOC_BIN := protoc
RM := rm
MKDIR := mkdir -p

generate-protobufs: clean-protobufs
	@echo "Generating python files from protobufs in $(PROTOBUF_SRC_DIR)"
	@$(MKDIR) $(PROTOBUF_OUT_DIR)
	@$(PROTOC_BIN) $(PROTOBUF_SRC_DIR)/*.proto --python_out=$(PROTOBUF_OUT_DIR) --proto_path=$(PROTOBUF_SRC_DIR)

clean-protobufs:
	@echo "Cleaning generated python files in $(PROTOBUF_OUT_DIR)"
	@$(RM) $(PROTOBUF_OUT_DIR)/*_pb2.py

